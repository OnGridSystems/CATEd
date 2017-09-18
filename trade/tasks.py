from __future__ import absolute_import, unicode_literals
import importlib
import re
import binascii
from json import JSONDecodeError

from ccxt import ExchangeNotAvailable, RequestTimeout
from celery.schedules import crontab
from celery.task import periodic_task
import datetime
from celery import shared_task
import time
import requests
from decimal import Decimal as _D
from django.conf import settings
from django.contrib.auth.models import User
from trade.models import UserExchange, UserBalance, Coin, Exchanges, Wallets, UserWallet, Transaction, UserHoldings
from yandex_money.api import Wallet, ExternalPayment
from tradeBOT.models import ExchangeCoin, Pair, ExchangeTicker, CoinMarketCupCoin, ExchangeMainCoin


def class_for_name(module_name, class_name):
    m = importlib.import_module(module_name)
    c = getattr(m, class_name)
    return c


@shared_task
def pull_exchanges_balances(ue_pk=None):
    if ue_pk is None:
        user_exchanges = UserExchange.objects.filter(is_active=True)
    else:
        user_exchanges = UserExchange.objects.filter(pk=ue_pk)
    if len(user_exchanges) > 0:
        for user_exchange in user_exchanges:
            exchange_object = class_for_name('ccxt', user_exchange.exchange.name)(
                {'apiKey': user_exchange.apikey, 'secret': user_exchange.apisecret})
            try:
                try:
                    balances = exchange_object.fetch_balance()
                    # print(balances)
                except binascii.Error:
                    user_exchange.error = 'Incorrect apikey or secret'
                    user_exchange.is_correct = False
                    user_exchange.is_active = False
                    user_exchange.save()
                    continue
                if balances:
                    total_btc = _D(0)
                    for item in balances.items():
                        if item[0] != 'info':
                            try:
                                user_coin = UserBalance.objects.get(ue=user_exchange, coin=item[0].lower())
                                user_coin.total = (item[1]['total'] if item[1]['total'] is not None else 0)
                                user_coin.btc_value, user_coin.conversions = fetch_btc_value(user_exchange.exchange,
                                                                                             item[0].lower(),
                                                                                             item[1]['total'])
                                user_coin.used = (item[1]['used'] if item[1]['used'] is not None else 0)
                                user_coin.free = (item[1]['free'] if item[1]['free'] is not None else 0)
                                user_coin.save()
                                total_btc += _D(user_coin.btc_value)
                            except UserBalance.DoesNotExist:
                                new_user_coin = UserBalance()
                                new_user_coin.ue = user_exchange
                                new_user_coin.coin = item[0].lower()
                                new_user_coin.total = (item[1]['total'] if not item[1]['total'] is None else 0)
                                new_user_coin.btc_value, new_user_coin.conversions = fetch_btc_value(
                                    user_exchange.exchange,
                                    item[0].lower(), item[1]['total'])
                                new_user_coin.used = (item[1]['used'] if item[1]['used'] is not None else 0)
                                new_user_coin.free = (item[1]['free'] if item[1]['free'] is not None else 0)
                                new_user_coin.save()
                                total_btc += _D(new_user_coin.btc_value)
                    user_exchange.total_btc = total_btc
                    user_exchange.total_usd = get_usd_value('btc', total_btc)
                    user_exchange.save()
            except ExchangeNotAvailable as e:
                # user_exchange.is_active = False
                # user_exchange.is_active_script = False
                user_exchange.error = e
                user_exchange.save()
            except RequestTimeout:
                continue
    return True


def fetch_btc_value(exchange, coin, amount=None, convertations=None):
    if amount is None:
        amount = 0
    if _D(amount) == _D(0):
        return 0, 'Null balance'
    if convertations is None:
        convertations = [coin + ' (' + str(_D(str(amount)).quantize(_D('.00000001'))) + ')']
    if coin.lower() == 'btc':
        return amount, '->'.join(convertations)
    try:
        coin = ExchangeCoin.objects.get(symbol=coin.lower(), exchange=exchange)
        # print('Нашел валюту: {}'.format(coin.symbol.upper()))
        try:
            # print('1Ищу пару BTC_{}'.format(coin.symbol.upper()))
            pair = Pair.objects.get(main_coin=ExchangeCoin.objects.get(symbol='btc', exchange=exchange),
                                    second_coin=coin)
            # print('1Нашел пару {}_{}'.format(pair.main_coin.symbol, pair.second_coin.symbol))
            ticker = ExchangeTicker.objects.filter(pair=pair, exchange=exchange).latest('date_time')
            # print('1Нашел тикер {} {}'.format(ticker, ticker.last))
            new_amount = _D(amount).quantize(_D('.00000001')) * _D(ticker.last).quantize(_D('.00000001'))
            convertations.append('btc (' + str(_D(str(new_amount)).quantize(_D('.00000001'))) + ')')
            return new_amount, '->'.join(convertations)
        except Pair.DoesNotExist:
            try:
                # print('2Ищу пару {}_BTC'.format(coin.symbol.upper()))
                pair = Pair.objects.get(second_coin=ExchangeCoin.objects.get(symbol='btc', exchange=exchange),
                                        main_coin=coin)
                # print('2Нашел пару {}_{}'.format(pair.main_coin.symbol, pair.second_coin.symbol))
                ticker = ExchangeTicker.objects.filter(pair=pair, exchange=exchange).latest('date_time')
                # print('2Нашел тикер {} {}'.format(ticker, ticker.last))
                new_amount = _D(amount).quantize(_D('.00000001')) / _D(ticker.last).quantize(_D('.00000001'))
                convertations.append('btc (' + str(_D(str(new_amount)).quantize(_D('.00000001'))) + ')')
                return new_amount, '->'.join(convertations)
            except Pair.DoesNotExist:
                try:
                    # print('3Ищу пару где вторая валюта {}'.format(coin.symbol.upper()))
                    pair = Pair.objects.get(second_coin=coin)
                    # print('3Нашел пару {}_{}'.format(pair.main_coin.symbol, pair.second_coin.symbol))
                    ticker = ExchangeTicker.objects.filter(pair=pair, exchange=exchange).latest('date_time')
                    # print('3Нашел тикер {} {}'.format(ticker, ticker.last))
                    in_first_coin = _D(ticker.last) * _D(amount)
                    convertations.append(
                        pair.main_coin.symbol + ' (' + str(_D(str(in_first_coin)).quantize(_D('.00000001'))) + ')')
                    fetch_btc_value(exchange, pair.main_coin.symbol, in_first_coin, convertations)
                except Pair.DoesNotExist:
                    # print('3Пара на найдена')
                    return 0, 'Not found'
                except ExchangeTicker.DoesNotExist:
                    # print("3Тикер не найден")
                    return 0, 'Not found'
            except ExchangeTicker.DoesNotExist:
                # print("2Тикер не найден")
                return 0, 'Not found'
        except ExchangeTicker.DoesNotExist:
            # print("1Тикер не найден")
            return 0, 'Not found'
    except ExchangeCoin.DoesNotExist:
        # print('Валюта не найдена')
        return 0, 'Not found'


@periodic_task(run_every=crontab(minute='*/1'))
def pull_exchanges_tickers():
    ExchangeTicker.objects.filter(
        date_time__lt=datetime.datetime.now() - datetime.timedelta(minutes=settings.TICKER_MINUTES_TO_CLEAR)).delete()
    exchanges = Exchanges.objects.all()
    for exchange in exchanges:
        exchange_object = class_for_name('ccxt', exchange.name)()
        try:
            for item, value in exchange_object.fetch_tickers().items():
                pair = re.match(r'([a-zA-Z0-9]+)/([a-zA-Z0-9]+)', item)
                try:
                    main_coin = ExchangeCoin.objects.get(exchange=exchange, symbol=pair.group(2))
                    second_coin = ExchangeCoin.objects.get(exchange=exchange, symbol=pair.group(1))
                    pair = Pair.objects.get(main_coin=main_coin, second_coin=second_coin)
                    new_ticker = ExchangeTicker()
                    new_ticker.exchange = exchange
                    new_ticker.pair = pair
                    new_ticker.high = value['high']
                    new_ticker.low = value['low']
                    new_ticker.bid = value['bid']
                    new_ticker.ask = value['ask']
                    new_ticker.base_volume = value['baseVolume']
                    new_ticker.last = value['last']
                    new_ticker.date_time = value['datetime']
                    new_ticker.save()
                except ExchangeCoin.DoesNotExist:
                    pass
                except Pair.DoesNotExist:
                    pass
        except ExchangeNotAvailable:
            continue
    # pull_exchanges_balances.delay()
    return True


@shared_task
def pull_exchanges():
    get_all_coins.delay()
    exchanges = Exchanges.objects.all()
    for exchange in exchanges:
        exchange_object = class_for_name('ccxt', exchange.name)()
        markets = exchange_object.fetch_markets()
        for item in markets:
            coins = [item['quote'], item['base']]
            for coin in coins:
                try:
                    market_cup_coin = CoinMarketCupCoin.objects.filter(symbol=coin.lower()).earliest('rank')
                    if market_cup_coin:
                        try:
                            old_coin = ExchangeCoin.objects.get(exchange=exchange, symbol=coin.lower())
                            old_coin.rank = market_cup_coin.rank
                            old_coin.save()
                        except ExchangeCoin.DoesNotExist:
                            new_coin = ExchangeCoin()
                            new_coin.exchange = exchange
                            new_coin.symbol = coin.lower()
                            new_coin.rank = market_cup_coin.rank
                            new_coin.save()
                except CoinMarketCupCoin.DoesNotExist:
                    pass
            try:
                coin = ExchangeCoin.objects.get(exchange=exchange, symbol=coins[0].lower())
                ExchangeMainCoin.objects.get_or_create(coin=coin)
            except ExchangeCoin.DoesNotExist:
                pass
            try:
                main_coin = ExchangeCoin.objects.get(exchange=exchange, symbol=coins[0].lower())
                second_coin = ExchangeCoin.objects.get(exchange=exchange, symbol=coins[1].lower())
                try:
                    old_pair = Pair.objects.get(main_coin=main_coin, second_coin=second_coin)
                    frozen = exchange.info_frozen_key
                    field = frozen.replace('-', '')
                    if frozen.startswith('-'):
                        old_pair.is_active = not bool(int(item['info'][field]))
                    else:
                        old_pair.is_active = bool(int(item['info'][field]))
                    old_pair.save()
                except Pair.DoesNotExist:
                    pair = Pair()
                    pair.main_coin = main_coin
                    pair.second_coin = second_coin
                    frozen = exchange.info_frozen_key
                    field = frozen.replace('-', '')
                    if frozen.startswith('-'):
                        pair.is_active = not bool(int(item['info'][field]))
                    else:
                        pair.is_active = bool(int(item['info'][field]))
                    pair.save()
            except ExchangeCoin.DoesNotExist:
                pass
    return True


@shared_task
def get_all_coins():
    response = requests.get('https://poloniex.com/public?command=returnCurrencies').json()
    for item in response:
        try:
            coin = Coin.objects.get(short_name=item)
        except Coin.DoesNotExist:
            new_coin = Coin()
            new_coin.short_name = item
            new_coin.full_name = response[item]['name']
            new_coin.save()
    return True


@periodic_task(run_every=crontab(minute='*/2'))
def get_eth_wallet_history():
    wallet, c = Wallets.objects.get_or_create(name='ETH')
    eth_uw = UserWallet.objects.filter(wallet=wallet)
    eth_to_btc = CryptoConvert('btc', 'eth')
    eth_to_usd = CryptoConvert('usd', 'eth')
    if len(eth_uw) > 0:
        for uw in eth_uw:
            balance = requests.get(
                'https://api.etherscan.io/api?module=account&action=balance&address=' + uw.address + '&tag=latest&apikey=18NX2UFSA1SUX76FFGHAGFBWNNAWK7KDNY').json()
            if balance['status'] == str(1):
                uw.balance = balance['result']
                uw.total_usd = eth_to_usd.convert('usd', 'eth', round(float(float(balance['result']) / (10 ** 18)), 8))
                uw.total_btc = eth_to_btc.convert('btc', 'eth', round(float(float(balance['result']) / (10 ** 18)), 8))
                uw.save()
            history = requests.get(
                'https://api.etherscan.io/api?module=account&action=txlist&address=' + uw.address + '&startblock=0&endblock=99999999&sort=desc&apikey=18NX2UFSA1SUX76FFGHAGFBWNNAWK7KDNY').json()
            if history['status'] == str(1):
                for item in history['result']:
                    try:
                        transaction = Transaction.objects.get(hash=item['hash'], name=uw.wallet.name + str(uw.pk))
                    except Transaction.MultipleObjectsReturned:
                        pass
                    except Transaction.DoesNotExist:
                        transaction = Transaction()
                        transaction.name = uw.wallet.name + str(uw.pk)
                        transaction.t_type = 'wallet'
                        transaction.number = item['blockNumber']
                        transaction.date = datetime.datetime.fromtimestamp(int(item['timeStamp'])).strftime(
                            '%Y-%m-%d %H:%M:%S')
                        transaction.t_from = item['from']
                        transaction.t_to = item['to']
                        transaction.currency = 'ETH'
                        if item['to'] == uw.address.lower():
                            transaction.type = 'in'
                        elif item['from'] == uw.address.lower():
                            transaction.type = 'out'
                        else:
                            transaction.type = 'unknown'
                        transaction.value = item['value']
                        transaction.usd_value = eth_to_usd.convert('usd', 'eth',
                                                                   round(float(float(item['value']) / (10 ** 18)), 8))
                        transaction.hash = item['hash']
                        transaction.block_hash = item['blockHash']
                        transaction.save()
        print('ok')
    else:
        print("Кошельки отсутствуют")
    return True


@periodic_task(run_every=crontab(minute='*/2'))
def get_btc_wallet_history():
    wallet, c = Wallets.objects.get_or_create(name='BTC')
    btc_uw = UserWallet.objects.filter(wallet=wallet)
    if len(btc_uw) > 0:
        for uw in btc_uw:
            btc_to_usd = CryptoConvert('usd', 'btc')
            data = requests.get('https://blockchain.info/ru/rawaddr/'+uw.address)
            try:
                transactions = data.json()
                if transactions:
                    uw.balance = transactions['final_balance'] / 100000000
                    uw.total_usd = btc_to_usd.convert('usd', 'btc', uw.balance)
                    uw.total_btc = uw.balance
                    uw.save()
                    for item in transactions['txs']:
                        try:
                            transaction = Transaction.objects.get(name=uw.wallet.name + str(uw.pk), hash=item['hash'])
                        except Transaction.MultipleObjectsReturned:
                            pass
                        except Transaction.DoesNotExist:
                            transaction = Transaction()
                            transaction.name = uw.wallet.name + str(uw.pk)
                            transaction.t_type = 'wallet'
                            transaction.number = item['tx_index']
                            transaction.date = datetime.datetime.fromtimestamp(item['time'])
                            transaction.currency = 'BTC'
                            t_from = ''
                            transaction.type = 'unknown'
                            for item_from in item['inputs']:
                                t_from += item_from['prev_out']['addr'] + '<br/>'
                                if item_from['prev_out']['addr'] == uw.address:
                                    transaction.type = 'out'
                                    transaction.value = _D(item_from['prev_out']['value']) / _D(100000000)
                            t_to = ''
                            for item_to in item['out']:
                                t_to += item_to['addr'] + '<br/>'
                                if item_to['addr'] == uw.address:
                                    transaction.type = 'in'
                                    transaction.value = _D(item_to['value']) / _D(100000000)
                            transaction.t_to = t_to
                            transaction.t_from = t_from
                            transaction.usd_value = btc_to_usd.convert('usd', 'btc', _D(transaction.value))
                            transaction.hash = item['hash']
                            transaction.block_hash = '-'
                            transaction.save()
            except JSONDecodeError as json_er:
                print('Ошибка разбора ответа: {}'.format(json_er))
                continue

    else:
        print("Кошельки отсутствуют")
    return True


@periodic_task(run_every=crontab(minute='*/2'))
def get_yandex_wallet_history():
    wallet, c = Wallets.objects.get_or_create(name='Yandex Money')
    yandex_uw = UserWallet.objects.filter(wallet=wallet)
    if len(yandex_uw) > 0:
        for uw in yandex_uw:
            access_token = uw.access_token
            if access_token is not None:
                yandex_wallet_object = Wallet(access_token)
                account_info = yandex_wallet_object.account_info()
                uw.balance = account_info['balance']
                uw.total_btc = get_btc_value('rur', account_info['balance'])
                uw.total_usd = get_usd_value('rur', account_info['balance'])
                uw.save()
                get_yandex_records(wallet=yandex_wallet_object, uw=uw)
        print('ok')
    else:
        print("Кошельки отсутствуют")
    return True


def get_yandex_records(wallet=None, uw=None, next_record=0):
    transactions = wallet.operation_history(
        {'start_record': int(next_record),
         'details': 'true',
         'records': 100})
    rur_to_usd = CryptoConvert('usd', 'rur')
    for t in transactions['operations']:
        try:
            transaction = Transaction.objects.get(name=uw.wallet.name + str(uw.pk), number=t['operation_id'])
        except Transaction.MultipleObjectsReturned:
            pass
        except Transaction.DoesNotExist:
            new_transaction = Transaction()
            new_transaction.name = uw.wallet.name + str(uw.pk)
            new_transaction.t_type = 'wallet'
            new_transaction.number = new_transaction.hash = t['operation_id']
            new_transaction.date = t['datetime']
            new_transaction.type = t['direction']
            new_transaction.currency = 'RUR'
            new_transaction.t_from = new_transaction.t_to = '-'
            if 'details' in t:
                if len(t['details']) > 0:
                    new_transaction.details = t['details']
            if 'title' in t:
                if len(t['title']) > 0:
                    new_transaction.title = t['title']
            new_transaction.value = t['amount']
            new_transaction.usd_value = rur_to_usd.convert('usd', 'rur', float(t['amount']))
            # new_transaction.usd_value = get_usd_value('rur', float(t['amount']))
            new_transaction.save()
    try:
        next_rec = transactions['next_record']
    except KeyError:
        next_rec = None
    if next_rec is not None:
        get_yandex_records(wallet, uw=uw, next_record=transactions['next_record'])


@periodic_task(run_every=crontab(minute='*/1'))
def calculate_holdings_history():
    date = datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S')
    users = User.objects.all()
    for user in users:
        wallets = UserWallet.objects.filter(user=user)
        if len(wallets) > 0:
            for wallet in wallets:
                holdings = UserHoldings()
                holdings.user = user
                holdings.type = 'Wallet@' + wallet.wallet.name + '(' + str(wallet.pk) + ')'
                holdings.total_btc = wallet.total_btc
                holdings.total_usd = wallet.total_usd
                holdings.date_time = date
                holdings.save()
        exchanges = UserExchange.objects.filter(user=user)
        if len(exchanges) > 0:
            for exchange in exchanges:
                holdings = UserHoldings()
                holdings.user = user
                holdings.type = 'Exchange@' + exchange.exchange.name + '(' + str(exchange.pk) + ')'
                holdings.total_btc = exchange.total_btc
                holdings.total_usd = exchange.total_usd
                holdings.date_time = date
                holdings.save()
    return True


def get_btc_value(coin_name=None, count=None):
    time.sleep(0.1)
    if not coin_name or not count:
        return 0
    else:
        if coin_name == 'dsh' or coin_name == 'DSH':
            coin_name = 'dash'
        response = requests.get('https://api.cryptonator.com/api/ticker/btc-' + coin_name.lower()).json()
        if response['success']:
            return float(count) / float(response['ticker']['price'])
        else:
            return 0


def get_usd_value(coin_name=None, count=None):
    time.sleep(0.1)
    if not coin_name or not count:
        return 0
    else:
        if coin_name == 'dsh' or coin_name == 'DSH':
            coin_name = 'dash'
        response = requests.get('https://api.cryptonator.com/api/ticker/usd-' + coin_name.lower()).json()
        if response['success']:
            return float(count) / float(response['ticker']['price'])
        else:
            return 0


class CryptoConvert:
    def __init__(self, coin_one_name, coin_two_name):
        if coin_two_name == 'dsh' or coin_two_name == 'DSH':
            coin_two_name = 'dash'
        if coin_one_name == 'dsh' or coin_one_name == 'DSH':
            coin_one_name = 'dash'
        self.coin_one_name = coin_one_name
        self.coin_two_name = coin_two_name
        self.price = None

    def get_price(self):
        if self.price is None:
            response = requests.get(
                'https://api.cryptonator.com/api/ticker/' + self.coin_one_name.lower() + '-' + self.coin_two_name.lower()).json()
            if response['success']:
                self.price = response['ticker']['price']
        return self.price

    def convert(self, coin_one_name, coin_two_name, count):
        if coin_one_name == self.coin_one_name and coin_two_name == self.coin_two_name:
            self.get_price()
        else:
            self.coin_one_name = coin_one_name
            self.coin_two_name = coin_two_name
            self.price = None
            self.get_price()
        return float(count) / float(self.price)
