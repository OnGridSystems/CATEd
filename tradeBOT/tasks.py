from __future__ import absolute_import, unicode_literals
import json
import re
from celery.schedules import crontab
from celery.task import periodic_task
import datetime
from celery import shared_task
import time
import requests
from channels import Group


from trade.models import Exchanges
from tradeBOT.models import ExchangeCoin, Pair, ExchangeMainCoin, CoinMarketCupCoin, ExchangeTicker


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


@periodic_task(run_every=datetime.timedelta(minutes=1))
def pull_poloniex_ticker():
    exchange = Exchanges.objects.get(exchange='poloniex')
    ticker = requests.get('https://poloniex.com/public?command=returnTicker').json()
    date_time = round_down(time.time())
    to_template = []
    for item in ticker:
        pair = re.match(r'([a-zA-Z0-9]+)_([a-zA-Z0-9]+)', item)
        try:
            main_coin = ExchangeCoin.objects.get(exchange=exchange, symbol=pair.group(1))
            second_coin = ExchangeCoin.objects.get(exchange=exchange, symbol=pair.group(2))
            pair = Pair.objects.get(main_coin=main_coin, second_coin=second_coin)
            new_ticker = ExchangeTicker()
            new_ticker.exchange = exchange
            new_ticker.pair = pair
            old_exch_ticker = ExchangeTicker.objects.filter(pair=pair, exchange=exchange, date_time__gt=int(datetime.date.today().strftime('%s'))).order_by('date_time').first()
            if old_exch_ticker is not None:
                old_last = old_exch_ticker.last
                new_last = ticker[item]['last']
                new_ticker.percent_change = round((float(new_last) - float(old_last)) / float(old_last), 8)
            new_ticker.high = ticker[item]['high24hr']
            new_ticker.low = ticker[item]['low24hr']
            new_ticker.bid = ticker[item]['highestBid']
            new_ticker.ask = ticker[item]['lowestAsk']
            new_ticker.base_volume = ticker[item]['baseVolume']
            new_ticker.last = ticker[item]['last']
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


@periodic_task(run_every=crontab(minute='*/1'))
def pull_bittrex_ticker():
    to_template = []
    exchange = Exchanges.objects.get(exchange='bittrex')
    ticker = requests.get('https://bittrex.com/api/v1.1/public/getmarketsummaries').json()
    date_time = round_down(time.time())
    for item in ticker['result']:
        pair_r = re.match(r'([a-zA-Z0-9]+)-([a-zA-Z0-9]+)', item['MarketName'])
        try:
            main_coin = ExchangeCoin.objects.get(exchange=exchange, symbol=pair_r.group(1))
            second_coin = ExchangeCoin.objects.get(exchange=exchange, symbol=pair_r.group(2))
            pair = Pair.objects.get(main_coin=main_coin, second_coin=second_coin)
            new_ticker = ExchangeTicker()
            new_ticker.exchange = exchange
            new_ticker.pair = pair
            old_exch_ticker = ExchangeTicker.objects.filter(pair=pair, exchange=exchange, date_time__gt=int(datetime.date.today().strftime('%s'))).order_by('date_time').first()
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


def round_down(x):
    x = int(x)
    return x - (x % 100)
