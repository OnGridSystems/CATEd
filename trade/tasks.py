from __future__ import absolute_import, unicode_literals
import os
import re

from celery.schedules import crontab
from celery.task import periodic_task
import datetime
from http.client import HTTPException
from celery import shared_task
import time
import requests
from decimal import Decimal
from django.contrib.auth.models import User
from trade.drivers.btce_driver import APIError
from trade.models import UserExchanges, UserBalance, Coin, Exchanges, Wallets, UserWallet, Transaction, UserHoldings
from trade.drivers import btce_trader, bittrex_driver
from poloniex import Poloniex, PoloniexCommandException
from yandex_money.api import Wallet, ExternalPayment


# @periodic_task(run_every=crontab(minute='*/5'))
# def start_trade_btce():
#     exchange = Exchanges.objects.get(exchange='btc-e')
#     btce_ue = UserExchanges.objects.filter(is_active=True, exchange=exchange)
#     if len(btce_ue) > 0:
#         for ue in btce_ue:
#             totalBtc = float(0)
#             try:
#                 driver = btce_trader.BtceTrader(secret=ue.apisecret, key=ue.apikey)
#                 try:
#                     balances = driver.pull_balances()
#                     if balances is not None:
#                         for item in balances['funds']:
#                             try:
#                                 user_coin = UserBalance.objects.get(ue=ue, coin=item.lower())
#                             except UserBalance.DoesNotExist:
#                                 user_coin = None
#                             if user_coin is None:
#                                 new_user_coin = UserBalance()
#                                 new_user_coin.ue = ue
#                                 new_user_coin.coin = item
#                                 new_user_coin.balance = balances['funds'][item]
#                                 btc_value = get_btc_value(coin_name=item, count=balances['funds'][item])
#                                 new_user_coin.btc_value = btc_value
#                                 totalBtc += btc_value
#                                 new_user_coin.save()
#                             else:
#                                 if user_coin.balance != balances['funds'][item]:
#                                     user_coin.balance = balances['funds'][item]
#                                     btc_value = get_btc_value(coin_name=item, count=balances['funds'][item])
#                                     user_coin.btc_value = btc_value
#                                     totalBtc += btc_value
#                                 else:
#                                     totalBtc += float(user_coin.btc_value)
#                                 user_coin.save()
#                         if 'open_orders' in balances:
#                             if balances['open_orders'] > 1:
#                                 on_orders_in_btc = add_money_on_orders(driver, ue)
#                             else:
#                                 on_orders_in_btc = 0
#                         else:
#                             on_orders_in_btc = 0
#                         ue.total_btc = totalBtc + on_orders_in_btc
#                         ue.total_usd = get_usd_value('btc', totalBtc + on_orders_in_btc)
#                         ue.save()
#                 except APIError as error:
#                     print(error)
#                     pass
#                     # print("Убираю накуй, неверно че-то")
#                     # ue.error = error
#                     # ue.is_active = False
#                     # ue.is_correct = False
#                     # ue.save()
#                 try:
#                     transactions = driver.trade_api.call('TransHistory')
#                     print(transactions)
#                     if len(transactions) > 0:
#                         for item in transactions:
#                             if int(transactions[item]['type']) == 1 or int(transactions[item]['type']) == 2:
#                                 try:
#                                     transaction = Transaction.objects.get(name=ue.exchange.exchange + str(ue.pk),
#                                                                           hash=item)
#                                 except Transaction.MultipleObjectsReturned:
#                                     pass
#                                 except Transaction.DoesNotExist:
#                                     new_trans = Transaction()
#                                     new_trans.name = ue.exchange.exchange + str(ue.pk)
#                                     new_trans.t_type = 'exchange'
#                                     new_trans.number = item
#                                     new_trans.hash = item
#                                     new_trans.details = transactions[item]['desc']
#                                     new_trans.date = datetime.datetime.fromtimestamp(
#                                         int(transactions[item]['timestamp'])).strftime(
#                                         '%Y-%m-%d %H:%M:%S')
#                                     new_trans.t_from = '-'
#                                     new_trans.t_to = '-'
#                                     if int(transactions[item]['type']) == 1:
#                                         new_trans.type = 'in'
#                                     elif int(transactions[item]['type']) == 2:
#                                         new_trans.type = 'out'
#                                     else:
#                                         new_trans.type = 'unknown'
#                                     new_trans.value = transactions[item]['amount']
#                                     new_trans.currency = transactions[item]['currency']
#                                     new_trans.usd_value = get_usd_value(transactions[item]['currency'],
#                                                                         transactions[item]['amount'])
#                                     new_trans.save()
#                 except Exception as error:
#                     print(error)
#             except HTTPException:
#                 print('Ошибка, начинаем заново')
#     else:
#         print("Никто не включил скрипт")
#     return True


def add_money_on_orders(driver, ue):
    orders = driver.pull_orders()
    on_orders_in_btc = float(0)
    for item in orders:
        amount = orders[item]['amount'] * orders[item]['rate']
        m = re.match(r'([a-zA-Z0-9]+)_([a-zA-Z0-9]+)', orders[item]['pair'])
        coin_name = m.group(2)
        coin_on_orders_in_btc = get_btc_value(coin_name, amount)
        try:
            user_coin = UserBalance.objects.get(ue=ue, coin=coin_name.lower())
            user_coin.balance += Decimal(amount)
            user_coin.btc_value += Decimal(coin_on_orders_in_btc)
            user_coin.save()
        except UserBalance.DoesNotExist:
            pass
        on_orders_in_btc += coin_on_orders_in_btc
    return on_orders_in_btc


@periodic_task(run_every=crontab(minute='*/5'))
def start_trade_poloniex():
    exchange = Exchanges.objects.get(exchange='poloniex')
    poloniex_ue = UserExchanges.objects.filter(is_active=True, exchange=exchange)
    if len(poloniex_ue) > 0:
        for ue in poloniex_ue:
            totalBtc = float(0)
            try:
                ue_apisecret = ue.apisecret.encode()
                driver = Poloniex(secret=ue_apisecret, apikey=ue.apikey)
                try:
                    balances = driver.returnCompleteBalances()
                    if balances is not None:
                        for c in balances.keys():
                            try:
                                user_coin = UserBalance.objects.get(ue=ue, coin=c.lower())
                            except UserBalance.DoesNotExist:
                                user_coin = None
                            if user_coin is None:
                                new_user_coin = UserBalance()
                                new_user_coin.ue = ue
                                new_user_coin.coin = c.lower()
                                new_user_coin.balance = float(balances[c]['available'])
                                new_user_coin.btc_value = float(balances[c]['btcValue'])
                                totalBtc += float(balances[c]['btcValue'])
                                new_user_coin.save()
                            else:
                                user_coin.balance = float(balances[c]['available'])
                                user_coin.btc_value = float(balances[c]['btcValue'])
                                totalBtc += float(balances[c]['btcValue'])
                                user_coin.save()
                    ue.total_btc = totalBtc
                    ue.total_usd = get_usd_value('btc', totalBtc)
                    ue.save()
                except PoloniexCommandException as error:
                    pass
                    # if error != 'Connection timed out. Please try again.':
                    #     ue.error = error
                    #     ue.is_active = False
                    #     ue.is_correct = False
                    #     ue.save()
                try:
                    deposits_and_withdrawals = driver.returnDepositsWithdrawals()
                    if len(deposits_and_withdrawals) > 0:
                        deposits = deposits_and_withdrawals['deposits']
                        if len(deposits) > 0:
                            for item in deposits:
                                try:
                                    transaction = Transaction.objects.get(name=ue.exchange.exchange + str(ue.pk),
                                                                          hash=item['txid'])
                                except Transaction.MultipleObjectsReturned:
                                    pass
                                except Transaction.DoesNotExist:
                                    new_trans = Transaction()
                                    new_trans.name = ue.exchange.exchange + str(ue.pk)
                                    new_trans.t_type = 'exchange'
                                    new_trans.number = item['confirmations']
                                    new_trans.hash = item['txid']
                                    new_trans.date = datetime.datetime.fromtimestamp(int(item['timestamp'])).strftime(
                                        '%Y-%m-%d %H:%M:%S')
                                    new_trans.t_from = '-'
                                    new_trans.t_to = item['address']
                                    new_trans.type = 'in'
                                    new_trans.value = item['amount']
                                    new_trans.currency = item['currency']
                                    new_trans.usd_value = get_usd_value(item['currency'], item['amount'])
                                    new_trans.save()
                        withdrawals = deposits_and_withdrawals['withdrawals']
                        # print(withdrawals)
                        if len(withdrawals) > 0:
                            for item in withdrawals:
                                try:
                                    transaction = Transaction.objects.get(name=ue.exchange.exchange + str(ue.pk),
                                                                          hash=item['withdrawalNumber'])
                                except Transaction.MultipleObjectsReturned:
                                    pass
                                except Transaction.DoesNotExist:
                                    new_trans = Transaction()
                                    new_trans.name = ue.exchange.exchange + str(ue.pk)
                                    new_trans.t_type = 'exchange'
                                    new_trans.number = item['withdrawalNumber']
                                    new_trans.hash = item['withdrawalNumber']
                                    new_trans.date = datetime.datetime.fromtimestamp(int(item['timestamp'])).strftime(
                                        '%Y-%m-%d %H:%M:%S')
                                    new_trans.t_from = '-'
                                    new_trans.t_to = item['address']
                                    new_trans.type = 'out'
                                    new_trans.value = item['amount']
                                    new_trans.currency = item['currency']
                                    new_trans.usd_value = get_usd_value(item['currency'], item['amount'])
                                    new_trans.save()
                except Exception as error:
                    print(error)

            except HTTPException:
                print('Ошибка, начинаем заново')
    else:
        print("Никто не включил скрипт")
    return True


@periodic_task(run_every=crontab(minute='*/5'))
def start_trade_bittrex():
    exchange = Exchanges.objects.get(exchange='bittrex')
    bittrex_ue = UserExchanges.objects.filter(is_active=True, exchange=exchange)
    if len(bittrex_ue) > 0:
        for ue in bittrex_ue:
            totalBtc = float(0)
            try:
                driver = bittrex_driver.Bittrex(api_secret=ue.apisecret, api_key=ue.apikey)
                try:
                    balances = driver.get_balances()
                    if balances['result'] is not None:
                        for c in balances['result']:
                            try:
                                user_coin = UserBalance.objects.get(ue=ue, coin=c['Currency'].lower())
                            except UserBalance.DoesNotExist:
                                user_coin = None
                            if user_coin is None:
                                new_user_coin = UserBalance()
                                new_user_coin.ue = ue
                                new_user_coin.coin = c['Currency'].lower()
                                new_user_coin.balance = float(c['Available'])
                                btc_value = get_btc_value(coin_name=c['Currency'].lower(), count=c['Balance'])
                                new_user_coin.btc_value = btc_value
                                totalBtc += btc_value
                                new_user_coin.save()
                            else:
                                user_coin.balance = float(c['Available'])
                                btc_value = get_btc_value(coin_name=c['Currency'].lower(), count=c['Balance'])
                                user_coin.btc_value = btc_value
                                totalBtc += btc_value
                                user_coin.save()
                    ue.total_btc = totalBtc
                    ue.total_usd = get_usd_value('btc', totalBtc)
                    ue.save()
                except Exception as error:
                    print(error)
                    pass
                    # print("Убираю накуй, неверно че-то")
                    # ue.error = error
                    # ue.is_active = False
                    # ue.is_correct = False
                    # ue.save()
                try:
                    deposits = driver.get_deposithistory()
                    for item in deposits['result']:
                        try:
                            transaction = Transaction.objects.get(name=ue.exchange.exchange + str(ue.pk),
                                                                  hash=item['TxId'])
                        except Transaction.MultipleObjectsReturned:
                            pass
                        except Transaction.DoesNotExist:
                            new_trans = Transaction()
                            new_trans.name = ue.exchange.exchange + str(ue.pk)
                            new_trans.t_type = 'exchange'
                            new_trans.number = item['Confirmations']
                            new_trans.hash = item['TxId']
                            trans_time = int(time.mktime(datetime.datetime.strptime(item['LastUpdated'],
                                                                                    "%Y-%m-%dT%H:%M:%S.%f").timetuple())) + 10800
                            new_trans.date = datetime.datetime.fromtimestamp(trans_time).strftime('%Y-%m-%d %H:%M:%S')
                            new_trans.t_from = '-'
                            new_trans.t_to = item['CryptoAddress']
                            new_trans.type = 'in'
                            new_trans.value = item['Amount']
                            new_trans.currency = item['Currency']
                            new_trans.usd_value = get_usd_value(item['Currency'], item['Amount'])
                            new_trans.save()
                except Exception as error:
                    print(error)
                try:
                    withdrawals = driver.get_withdrawalhistory()
                    for item in withdrawals['result']:
                        try:
                            transaction = Transaction.objects.get(name=ue.exchange.exchange + str(ue.pk),
                                                                  hash=item['TxId'])
                        except Transaction.MultipleObjectsReturned:
                            pass
                        except Transaction.DoesNotExist:
                            new_trans = Transaction()
                            new_trans.name = ue.exchange.exchange + str(ue.pk)
                            new_trans.t_type = 'exchange'
                            new_trans.number = item['Confirmations']
                            new_trans.hash = item['TxId']
                            new_trans.date = item['LastUpdated']
                            new_trans.t_from = '-'
                            new_trans.t_to = item['CryptoAddress']
                            new_trans.type = 'in'
                            new_trans.value = item['Amount']
                            new_trans.currency = item['Currency']
                            new_trans.usd_value = get_usd_value(item['Currency'], item['Amount'])
                            new_trans.save()
                except Exception as error:
                    print(error)
            except HTTPException:
                print('Ошибка, начинаем заново')
    else:
        print("Никто не включил скрипт")
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
    wallet = Wallets.objects.get(name='ETH')
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
                        if item['to'] == uw.address:
                            transaction.type = 'in'
                        elif item['from'] == uw.address:
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
    wallet = Wallets.objects.get(name='BTC')
    btc_uw = UserWallet.objects.filter(wallet=wallet)
    if len(btc_uw) > 0:
        for uw in btc_uw:
            btc_to_usd = CryptoConvert('usd', 'btc')
            balance = requests.get('http://btc.blockr.io/api/v1/address/balance/' + uw.address).json()
            if balance['status'] == 'success':
                uw.balance = balance['data']['balance']
                # uw.total_usd = get_usd_value('btc', balance['data']['balance'])
                uw.total_usd = btc_to_usd.convert('usd', 'btc', balance['data']['balance'])
                uw.total_btc = balance['data']['balance']
                uw.save()
            history = requests.get(
                'http://btc.blockr.io/api/v1/address/txs/' + uw.address).json()
            if history:
                if history['status'] == 'success':
                    for item in history['data']['txs']:
                        try:
                            transaction = Transaction.objects.get(name=uw.wallet.name + str(uw.pk), hash=item['tx'])
                        except Transaction.MultipleObjectsReturned:
                            pass
                        except Transaction.DoesNotExist:
                            tx_his = requests.get('https://btc.blockr.io/api/v1/tx/info/' + item['tx']).json()
                            if tx_his['status'] == 'success':
                                transaction = Transaction()
                                transaction.name = uw.wallet.name + str(uw.pk)
                                transaction.t_type = 'wallet'
                                transaction.number = tx_his['data']['block']
                                transaction.date = tx_his['data']['time_utc']
                                transaction.currency = 'BTC'
                                if float(item['amount']) > 0:
                                    t_from = ''
                                    for item_from in tx_his['data']['trade']['vins']:
                                        t_from += item_from['address'] + '<br/>'
                                    t_to = uw.address
                                else:
                                    t_from = uw.address
                                    t_to = ''
                                    for item_to in tx_his['data']['trade']['vouts']:
                                        t_to += item_to['address'] + '<br/>'
                                transaction.t_to = t_to
                                transaction.t_from = t_from
                                if t_to == uw.address:
                                    transaction.type = 'in'
                                elif t_from == uw.address:
                                    transaction.type = 'out'
                                else:
                                    transaction.type = 'unknown'
                                transaction.value = item['amount']
                                # transaction.usd_value = get_usd_value('btc', float(item['amount']))
                                transaction.usd_value = btc_to_usd.convert('usd', 'btc', float(item['amount']))
                                transaction.hash = item['tx']
                                transaction.block_hash = '-'
                                transaction.save()
    else:
        print("Кошельки отсутствуют")
    return True


@periodic_task(run_every=crontab(minute='*/2'))
def get_yandex_wallet_history():
    wallet = Wallets.objects.get(name='Yandex Money')
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
        exchanges = UserExchanges.objects.filter(user=user)
        if len(exchanges) > 0:
            for exchange in exchanges:
                holdings = UserHoldings()
                holdings.user = user
                holdings.type = 'Exchange@' + exchange.exchange.exchange + '(' + str(exchange.pk) + ')'
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


def get_btc_value_from_btce(coin_name=None, count=None):
    if not coin_name or not count:
        return 0
    else:
        response = requests.get('https://btc-e.nz/api/3/ticker/btc_' + coin_name.lower()).json()
        if response:
            print(float(count) / float(response['btc_' + coin_name.lower()]['last']))
            return float(count) / float(response['btc_' + coin_name.lower()]['last'])
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
