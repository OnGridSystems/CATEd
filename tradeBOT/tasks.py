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
from trade.drivers.btce_driver import APIError
from trade.drivers import btce_trader, bittrex_driver
from poloniex import Poloniex, PoloniexCommandException
from yandex_money.api import Wallet, ExternalPayment

from trade.models import Exchanges
from tradeBOT.models import ExchangeCoin, Pair, ExchangeMainCoin, CoinMarketCupCoin


@shared_task
def pull_poloniex():
    exchange = Exchanges.objects.get(exchange='poloniex')
    coins = requests.get('https://poloniex.com/public?command=returnCurrencies').json()
    for coin in coins:
        try:
            coin_in_100 = CoinMarketCupCoin.objects.get(symbol=coin)
            if coin_in_100.rank <= 100:
                try:
                    old_coin = ExchangeCoin.objects.get(exchange=exchange, symbol=coin)
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


@shared_task
def pull_bittrex():
    exchange = Exchanges.objects.get(exchange='bittrex')
    coins = requests.get('https://bittrex.com/api/v1.1/public/getcurrencies').json()
    for coin in coins['result']:
        try:
            coin_in_100 = CoinMarketCupCoin.objects.get(symbol=coin['Currency'])
            if coin_in_100.rank <= 100:
                try:
                    old_coin = ExchangeCoin.objects.get(exchange=exchange, symbol=coin['Currency'])
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


@shared_task
def pull_btce():
    exchange = Exchanges.objects.get(exchange='btc-e')
    coins = requests.get('https://btc-e.nz/api/3/info').json()
    pairs = list(coins['pairs'].keys())
    for item in pairs:
        pair = re.match(r'([a-zA-Z0-9]+)_([a-zA-Z0-9]+)', item)
        if pair:
            try:
                main_coin_in_top = CoinMarketCupCoin.objects.get(symbol=pair.group(1))
                if main_coin_in_top:
                    try:
                        main_coin_exist = ExchangeCoin.objects.get(exchange=exchange, symbol=pair.group(1))
                    except ExchangeCoin.DoesNotExist:
                        new_coin = ExchangeCoin()
                        new_coin.exchange = exchange
                        new_coin.name = main_coin_in_top.name
                        new_coin.symbol = pair.group(1)
                        new_coin.is_active = not coins['pairs'][item]['hidden']
                        new_coin.save()
                        try:
                            old_primary_coin = ExchangeMainCoin.objects.get(coin=new_coin)
                        except ExchangeMainCoin.DoesNotExist:
                            new_primary_coin = ExchangeMainCoin()
                            new_primary_coin.coin = new_coin
                            new_primary_coin.total = 0
                            new_primary_coin.save()
                second_coin_in_top = CoinMarketCupCoin.objects.get(symbol=pair.group(2))
                if second_coin_in_top:
                    try:
                        second_coin_exist = ExchangeCoin.objects.get(exchange=exchange, symbol=pair.group(2))
                    except ExchangeCoin.DoesNotExist:
                        new_coin = ExchangeCoin()
                        new_coin.exchange = exchange
                        new_coin.name = second_coin_in_top.name
                        new_coin.symbol = pair.group(2)
                        new_coin.is_active = not coins['pairs'][item]['hidden']
                        new_coin.save()
            except CoinMarketCupCoin.DoesNotExist:
                pass
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
    return True


@shared_task
def pull_coinmarketcup():
    response = requests.get('https://api.coinmarketcap.com/v1/ticker/').json()
    if 'error' not in response:
        for item in response:
            if int(item['rank']) <= 100:
                try:
                    old_coinmarket_coin = CoinMarketCupCoin.objects.get(name=item['name'])
                    old_coinmarket_coin.price_usd = item['price_usd']
                    old_coinmarket_coin.volume_usd_24h = item['24h_volume_usd']
                    old_coinmarket_coin.available_supply = item['available_supply']
                    old_coinmarket_coin.total_supply = item['total_supply']
                    old_coinmarket_coin.save()
                except CoinMarketCupCoin.DoesNotExist:
                    new_coin = CoinMarketCupCoin()
                    new_coin.name = item['name']
                    new_coin.symbol = item['symbol']
                    new_coin.rank = item['rank']
                    new_coin.price_usd = item['price_usd']
                    new_coin.volume_usd_24h = item['24h_volume_usd']
                    new_coin.available_supply = item['available_supply']
                    new_coin.total_supply = item['total_supply']
                    new_coin.save()
    return True
