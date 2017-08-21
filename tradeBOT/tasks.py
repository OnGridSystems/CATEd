from __future__ import absolute_import, unicode_literals
import json
import re

import _thread

import websocket
from django.db.models import Q
from http.client import HTTPException
import sys
from decimal import Decimal as D, getcontext, setcontext, Context, localcontext
from celery.schedules import crontab
from celery.task import periodic_task
import datetime
from celery import shared_task
import time
import requests
from channels import Group
from poloniex import Poloniex
from trade.models import Exchanges, UserExchanges, UserBalance
from tradeBOT.models import ExchangeCoin, Pair, ExchangeMainCoin, CoinMarketCupCoin, ExchangeTicker, Order, UserPair, \
    ToTrade, UserMainCoinPriority
from django.conf import settings


@periodic_task(run_every=datetime.timedelta(hours=1))
def pull_poloniex():
    exchange = Exchanges.objects.get(exchange='poloniex')
    coins = requests.get('https://poloniex.com/public?command=returnCurrencies').json()
    for coin in coins:
        try:
            coin_in_100 = CoinMarketCupCoin.objects.get(symbol=coin)
            if coin_in_100.rank <= 100:
                try:
                    old_coin = ExchangeCoin.objects.get(exchange=exchange, symbol=coin)
                    old_coin.is_active = bool(not coins[coin]['disabled'])
                    old_coin.save()
                except ExchangeCoin.DoesNotExist:
                    new_coin = ExchangeCoin()
                    new_coin.exchange = exchange
                    new_coin.symbol = coin
                    new_coin.name = coins[coin]['name']
                    new_coin.is_active = bool(not coins[coin]['disabled'])
                    new_coin.save()
        except CoinMarketCupCoin.DoesNotExist:
            pass
    pairs = requests.get('https://poloniex.com/public?command=return24hVolume').json()
    for item in pairs:
        pair = re.match(r'([a-zA-Z0-9]+)_([a-zA-Z0-9]+)', item)
        if pair:
            try:
                main_coin = ExchangeCoin.objects.get(exchange=exchange, symbol=pair.group(1))
                second_coin = ExchangeCoin.objects.get(exchange=exchange, symbol=pair.group(2))
                if main_coin and second_coin:
                    try:
                        old_pair = Pair.objects.get(main_coin=main_coin, second_coin=second_coin)
                    except Pair.DoesNotExist:
                        new_pair = Pair()
                        new_pair.main_coin = main_coin
                        new_pair.second_coin = second_coin
                        new_pair.save()
            except ExchangeCoin.DoesNotExist:
                pass
        else:
            primary_coin = re.match(r'total([a-zA-Z0-9]+)', item)
            if primary_coin:
                try:
                    old_coin = ExchangeCoin.objects.get(exchange=exchange, symbol=primary_coin.group(1))
                    old_primary_coin = ExchangeMainCoin.objects.get(coin=old_coin)
                except ExchangeCoin.DoesNotExist:
                    pass
                except ExchangeMainCoin.DoesNotExist:
                    new_primary_coin = ExchangeMainCoin()
                    new_primary_coin.coin = old_coin
                    new_primary_coin.total = pairs[item]
                    new_primary_coin.save()
    return True


@periodic_task(run_every=datetime.timedelta(hours=1))
def pull_bittrex():
    exchange = Exchanges.objects.get(exchange='bittrex')
    coins = requests.get('https://bittrex.com/api/v1.1/public/getcurrencies').json()
    for coin in coins['result']:
        try:
            coin_in_100 = CoinMarketCupCoin.objects.get(symbol=coin['Currency'])
            if coin_in_100.rank <= 100:
                try:
                    old_coin = ExchangeCoin.objects.get(exchange=exchange, symbol=coin['Currency'])
                    old_coin.is_active = bool(coin['IsActive'])
                    old_coin.save()
                except ExchangeCoin.DoesNotExist:
                    new_coin = ExchangeCoin()
                    new_coin.exchange = exchange
                    new_coin.symbol = coin['Currency']
                    new_coin.name = coin['CurrencyLong']
                    new_coin.is_active = bool(coin['IsActive'])
                    new_coin.save()
        except CoinMarketCupCoin.DoesNotExist:
            pass
    pairs = requests.get('https://bittrex.com/api/v1.1/public/getmarkets').json()
    for pair in pairs['result']:
        if pair:
            try:
                main_coin = ExchangeCoin.objects.get(exchange=exchange, symbol=pair['BaseCurrency'])
                if main_coin:
                    try:
                        primary_coin = ExchangeMainCoin.objects.get(coin=main_coin)
                    except ExchangeMainCoin.DoesNotExist:
                        new_primary_coin = ExchangeMainCoin()
                        new_primary_coin.coin = main_coin
                        new_primary_coin.total = 0
                        new_primary_coin.save()
                second_coin = ExchangeCoin.objects.get(exchange=exchange, symbol=pair['MarketCurrency'])
                if main_coin and second_coin:
                    try:
                        old_pair = Pair.objects.get(main_coin=main_coin, second_coin=second_coin)
                    except Pair.DoesNotExist:
                        new_pair = Pair()
                        new_pair.main_coin = main_coin
                        new_pair.second_coin = second_coin
                        new_pair.save()
            except ExchangeCoin.DoesNotExist:
                pass
    return True


# @shared_task
# def pull_btce():
#     exchange = Exchanges.objects.get(exchange='btc-e')
#     coins = requests.get('https://btc-e.nz/api/3/info').json()
#     pairs = list(coins['pairs'].keys())
#     for item in pairs:
#         pair = re.match(r'([a-zA-Z0-9]+)_([a-zA-Z0-9]+)', item)
#         if pair:
#             try:
#                 main_coin_in_top = CoinMarketCupCoin.objects.get(symbol=pair.group(1))
#                 if main_coin_in_top:
#                     try:
#                         main_coin_exist = ExchangeCoin.objects.get(exchange=exchange, symbol=pair.group(1))
#                     except ExchangeCoin.DoesNotExist:
#                         new_coin = ExchangeCoin()
#                         new_coin.exchange = exchange
#                         new_coin.name = main_coin_in_top.name
#                         new_coin.symbol = pair.group(1)
#                         new_coin.is_active = not coins['pairs'][item]['hidden']
#                         new_coin.save()
#                         try:
#                             old_primary_coin = ExchangeMainCoin.objects.get(coin=new_coin)
#                         except ExchangeMainCoin.DoesNotExist:
#                             new_primary_coin = ExchangeMainCoin()
#                             new_primary_coin.coin = new_coin
#                             new_primary_coin.total = 0
#                             new_primary_coin.save()
#                 second_coin_in_top = CoinMarketCupCoin.objects.get(symbol=pair.group(2))
#                 if second_coin_in_top:
#                     try:
#                         second_coin_exist = ExchangeCoin.objects.get(exchange=exchange, symbol=pair.group(2))
#                     except ExchangeCoin.DoesNotExist:
#                         new_coin = ExchangeCoin()
#                         new_coin.exchange = exchange
#                         new_coin.name = second_coin_in_top.name
#                         new_coin.symbol = pair.group(2)
#                         new_coin.is_active = not coins['pairs'][item]['hidden']
#                         new_coin.save()
#             except CoinMarketCupCoin.DoesNotExist:
#                 pass
#             try:
#                 main_coin = ExchangeCoin.objects.get(exchange=exchange, symbol=pair.group(1))
#                 second_coin = ExchangeCoin.objects.get(exchange=exchange, symbol=pair.group(2))
#                 if main_coin and second_coin:
#                     try:
#                         old_pair = Pair.objects.get(main_coin=main_coin, second_coin=second_coin)
#                     except Pair.DoesNotExist:
#                         new_pair = Pair()
#                         new_pair.main_coin = main_coin
#                         new_pair.second_coin = second_coin
#                         new_pair.save()
#             except ExchangeCoin.DoesNotExist:
#                 pass
#     return True


@shared_task
def pull_coinmarketcup():
    response = requests.get('https://api.coinmarketcap.com/v1/ticker/?limit=100').json()
    if 'error' not in response:
        for item in response:
            try:
                old_coinmarket_coin = CoinMarketCupCoin.objects.get(symbol=item['symbol'])
                old_coinmarket_coin.coin_market_id = item['id']
                old_coinmarket_coin.name = item['name']
                old_coinmarket_coin.price_usd = item['price_usd']
                old_coinmarket_coin.rank = item['rank']
                old_coinmarket_coin.volume_usd_24h = item['24h_volume_usd']
                old_coinmarket_coin.available_supply = item['available_supply']
                old_coinmarket_coin.total_supply = item['total_supply']
                old_coinmarket_coin.save()
            except CoinMarketCupCoin.DoesNotExist:
                new_coin = CoinMarketCupCoin()
                new_coin.coin_market_id = item['id']
                new_coin.name = item['name']
                new_coin.symbol = item['symbol']
                new_coin.rank = item['rank']
                new_coin.price_usd = item['price_usd']
                new_coin.volume_usd_24h = item['24h_volume_usd']
                new_coin.available_supply = item['available_supply']
                new_coin.total_supply = item['total_supply']
                new_coin.save()
    return True


# @periodic_task(run_every=datetime.timedelta(seconds=10))
@shared_task
def pull_poloniex_ticker():
    # exchange = Exchanges.objects.get(exchange='poloniex')
    # ticker = requests.get('https://poloniex.com/public?command=returnTicker').json()
    # date_time = round_down(time.time(), 1)
    # to_template = []
    # for item in ticker:
    #     pair = re.match(r'([a-zA-Z0-9]+)_([a-zA-Z0-9]+)', item)
    #     try:
    #         main_coin = ExchangeCoin.objects.get(exchange=exchange, symbol=pair.group(1))
    #         second_coin = ExchangeCoin.objects.get(exchange=exchange, symbol=pair.group(2))
    #         pair = Pair.objects.get(main_coin=main_coin, second_coin=second_coin)
    #         new_ticker = ExchangeTicker()
    #         new_ticker.exchange = exchange
    #         new_ticker.pair = pair
    #         old_exch_ticker = ExchangeTicker.objects.filter(pair=pair, exchange=exchange, date_time__gt=int(
    #             datetime.date.today().strftime('%s'))).order_by('date_time').first()
    #         if old_exch_ticker is not None:
    #             old_last = old_exch_ticker.last
    #             new_last = ticker[item]['last']
    #             new_ticker.percent_change = round((float(new_last) - float(old_last)) / float(old_last), 8)
    #         new_ticker.high = ticker[item]['high24hr']
    #         new_ticker.low = ticker[item]['low24hr']
    #         new_ticker.bid = ticker[item]['highestBid']
    #         new_ticker.ask = ticker[item]['lowestAsk']
    #         new_ticker.base_volume = ticker[item]['baseVolume']
    #         new_ticker.last = ticker[item]['last']
    #         new_ticker.date_time = date_time
    #         new_ticker.save()
    #         pair_temp = {'pair_id': pair.pk, 'last': new_ticker.last,
    #                      'percent': round(new_ticker.percent_change * 100, 2)}
    #         to_template.append(pair_temp)
    #     except ExchangeCoin.DoesNotExist:
    #         pass
    #     except Pair.DoesNotExist:
    #         pass
    # calculate_to_trade.delay()
    # if len(to_template) > 0:
    #     Group("trade").send({'text': json.dumps(to_template)})
    # return True

    exchange = Exchanges.objects.get(exchange='poloniex')
    ticker = requests.get('https://poloniex.com/public?command=returnTicker').json()
    markets = {}
    for item in ticker:
        pair = re.match(r'([a-zA-Z0-9]+)_([a-zA-Z0-9]+)', item)
        try:
            main_coin = ExchangeCoin.objects.get(exchange=exchange, symbol=pair.group(1))
            second_coin = ExchangeCoin.objects.get(exchange=exchange, symbol=pair.group(2))
            pair = Pair.objects.get(main_coin=main_coin, second_coin=second_coin)
            market = {ticker[item]['id']: pair.pk}
            markets.update(market)
        except ExchangeCoin.DoesNotExist:
            pass
        except Pair.DoesNotExist:
            pass


@periodic_task(run_every=datetime.timedelta(seconds=10))
def pull_bittrex_ticker():
    to_template = []
    exchange = Exchanges.objects.get(exchange='bittrex')
    ticker = requests.get('https://bittrex.com/api/v1.1/public/getmarketsummaries').json()
    date_time = round_down(time.time(), 1)
    for item in ticker['result']:
        pair_r = re.match(r'([a-zA-Z0-9]+)-([a-zA-Z0-9]+)', item['MarketName'])
        try:
            main_coin = ExchangeCoin.objects.get(exchange=exchange, symbol=pair_r.group(1))
            second_coin = ExchangeCoin.objects.get(exchange=exchange, symbol=pair_r.group(2))
            pair = Pair.objects.get(main_coin=main_coin, second_coin=second_coin)
            new_ticker = ExchangeTicker()
            new_ticker.exchange = exchange
            new_ticker.pair = pair
            old_exch_ticker = ExchangeTicker.objects.filter(pair=pair, exchange=exchange, date_time__gt=int(
                datetime.date.today().strftime('%s'))).order_by('date_time').first()
            if old_exch_ticker is not None:
                old_last = old_exch_ticker.last
                new_last = item['Last']
                new_ticker.percent_change = round((float(new_last) - float(old_last)) / float(old_last), 8)
            new_ticker.high = item['High']
            new_ticker.low = item['Low']
            new_ticker.bid = item['Bid']
            new_ticker.ask = item['Ask']
            new_ticker.base_volume = item['BaseVolume']
            new_ticker.last = item['Last']
            new_ticker.date_time = date_time
            new_ticker.save()
            pair_temp = {'pair_id': pair.pk, 'last': new_ticker.last,
                         'percent': round(new_ticker.percent_change * 100, 2)}
            to_template.append(pair_temp)
        except ExchangeCoin.DoesNotExist:
            pass
        except Pair.DoesNotExist:
            pass
    if len(to_template) > 0:
        Group("trade").send({'text': json.dumps(to_template)})
    return True


def round_down(x, s):
    x = int(x)
    return x - (x % (10 * s))


@periodic_task(run_every=datetime.timedelta(minutes=settings.TICKER_MINUTES_TO_CLEAR))
def clean_ticker():
    ExchangeTicker.objects.filter(
        date_time__lt=datetime.datetime.now() - datetime.timedelta(minutes=settings.TICKER_MINUTES_TO_CLEAR)).delete()


@shared_task
def pull_poloniex_orders():
    getcontext().rounding = 'ROUND_DOWN'
    exchange = Exchanges.objects.get(exchange='poloniex')
    poloniex_ue = UserExchanges.objects.filter(pk=4)
    if len(poloniex_ue) > 0:
        for ue in poloniex_ue:
            try:
                ue_apisecret = ue.apisecret.encode()
                driver = Poloniex(secret=ue_apisecret, apikey=ue.apikey)
                orders = driver.returnTradeHistory(start=1, end=9999999999)
                total_naeb = {}
                for item in orders:
                    pair = re.match(r'([a-zA-Z0-9]+)_([a-zA-Z0-9]+)', item)
                    total_naeb[pair.group(1)] = 0
                    for order in orders[item]:
                        try:
                            e_order = Order.objects.get(orderNumber=order['tradeID'])
                        except Order.DoesNotExist:
                            n_order = Order()
                            n_order.ue = ue
                            n_order.pair = item
                            n_order.globalTradeID = order['globalTradeID']
                            n_order.type = order['type']
                            n_order.total = order['total']
                            n_order.amount = order['amount']
                            n_order.tradeID = order['tradeID']
                            n_order.date_time = order['date']
                            n_order.category = order['category']
                            n_order.orderNumber = order['orderNumber']
                            n_order.fee = order['fee']
                            n_order.rate = order['rate']
                            total = (D(order['rate']) * D(order['amount'])).quantize(D('.000000001'))
                            if total.quantize(D('.00000001')) != D(str(order['total'])):
                                total = round(float(total), 8)
                            n_order.our_total = total
                            n_order.save()
            except HTTPException:
                print('Ошибка, начинаем заново')
    else:
        pass
    return True


@shared_task
def calculate_to_trade():
    pass
    # getcontext().rounding = 'ROUND_DOWN'
    # user_pairs = UserPair.objects.filter(
    #     ~Q(change_percent=0) & ~Q(change_interval=0) & Q(user_exchange__is_active_script=True))
    # for item in user_pairs:
    #     # смотрим сколько у нас первой валюты
    #     user_have_main_coin = UserBalance.objects.get(ue=item.user_exchange, coin=item.pair.main_coin.symbol.lower())
    #
    #     # считаем сколько можно купить второй валюты в паре
    #     user_have_second_coin = UserBalance.objects.get(ue=item.user_exchange,
    #                                                     coin=item.pair.second_coin.symbol.lower())
    #     user_have_second_coin_in_percent = user_have_second_coin.btc_value / (item.user_exchange.total_btc / 100)
    #     may_buy = item.share - user_have_second_coin_in_percent
    #     print(may_buy)
    #     if may_buy > 0:
    #         try:
    #             user_main_coin = UserMainCoinPriority.objects.get(main_coin__coin=item.pair.main_coin,
    #                                                               user_exchange=item.user_exchange)
    #             is_active = user_main_coin.is_active
    #         except UserMainCoinPriority.DoesNotExist:
    #             is_active = True
    #         if is_active:
    #             try:
    #                 ticker = ExchangeTicker.objects.filter(pair=item.pair,
    #                                                        date_time__gte=round_down(time.time(),
    #                                                                                  1) - item.change_interval,
    #                                                        date_time__lte=round_down(time.time(),
    #                                                                                  1) - item.change_interval + 22).earliest(
    #                     'date_time')
    #                 last_ticker = ExchangeTicker.objects.filter(pair=item.pair).latest('date_time')
    #             except ExchangeTicker.DoesNotExist:
    #                 continue
    #             if ticker is not None and last_ticker is not None:
    #                 # print('Last: ' + str(ticker.pk) + ' -- ' + str(ticker.last))
    #                 # print('Current: ' + str(last_ticker.pk) + ' -- ' + str(last_ticker.last))
    #                 change_percent = (last_ticker.last - ticker.last) / ticker.last
    #                 # print('Change percent' + str(change_percent))
    #                 order_type = 'up' if change_percent > 0 else 'down'
    #                 need_to_write = True
    #                 try:
    #                     last_to_trade = ToTrade.objects.filter(user_pair=item).latest('date_created')
    #                     if last_to_trade.type == order_type:
    #                         need_to_write = False
    #                 except ToTrade.DoesNotExist:
    #                     pass
    #                 if abs(change_percent * 100) >= item.change_percent and need_to_write:
    #                     to_trade = ToTrade()
    #                     to_trade.percent_react = change_percent
    #                     to_trade.user_pair = item
    #                     to_trade.type = order_type
    #                     to_trade.price = last_ticker.last
    #                     amount = min(user_have_main_coin.balance, ((item.user_exchange.total_btc / 100) * may_buy))
    #                     to_trade.amount = amount / last_ticker.last
    #                     # Высчитываю сколько это должно стоить по версии poloniex'a
    #                     total = D(str(amount)).quantize(D('.000000001'))
    #                     if int(total * 100000000 % 10) < 9:
    #                         total = D(str(round(float(total), 8)))
    #                     else:
    #                         total = total.quantize(D('.00000001'))
    #                     to_trade.total = total
    #                     fee = D('0.0015') if change_percent < 0 else D('0.0025')
    #                     to_trade.total_f = total - (total * fee)
    #                     to_trade.fee = fee
    #                     to_trade.cause = 'Got into the conditions'
    #                     to_trade.save()
    # return True
