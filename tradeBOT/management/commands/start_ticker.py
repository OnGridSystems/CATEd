from __future__ import absolute_import, unicode_literals
import asyncio
import datetime
import time
import json
import re
import threading
import urllib
import urllib.request
from collections import OrderedDict
import websockets
from django.core.management.base import BaseCommand, CommandError
from channels import Group
from django.db.models import Sum
import pickle
from django.conf import settings
import jsonpickle

from trade.models import Exchanges, UserBalance
from tradeBOT.models import ExchangeCoin, Pair, ExchangeTicker, UserPair, UserMainCoinPriority, UserCoinShare
from decimal import Decimal as _D
import warnings
from tradeBOT.tasks import start_calculate_poloniex_buy, start_calculate_poloniex_sell
from django.core.serializers.json import DjangoJSONEncoder

warnings.filterwarnings(
    'ignore', r"DateTimeField .* received a naive datetime",
    RuntimeWarning, r'django\.db\.models\.fields')


class Command(BaseCommand):
    help = 'Init poloniex ticker read'

    def handle(self, *args, **options):
        """ Do your work here """
        sub = PoloniexSubscriber()
        sub.start_subscribe()
        try:
            while True:
                pass
        except KeyboardInterrupt:
            # quit
            pass


GET_TICKERS_URL = 'https://poloniex.com/public?command=returnTicker'
API_LINK = 'wss://api2.poloniex.com'
SUBSCRIBE_COMMAND = '{"command":"subscribe","channel":$}'
TICKER_SUBSCRIBE = 1002
TICKER_OUTPUT = 'TICKER UPDATE {}={}(last),{}(lowestAsk),{}(highestBid),{}(percentChange),{}(baseVolume),{}(quoteVolume),{}(isFrozen),{}(high24hr),{}(low24hr)'
TRADE_OUTPUT = 'TRADE {}={}(tradeId),{}(bookSide),{}(price),{}(size),{}(timestamp)'


class PoloniexSubscriber(object):
    def __init__(self):
        self._tickers_list = {}
        self._markets_list = []
        self._tickers_id = {}
        tickers_data = self._get_all_tickers()
        for ticker, data in tickers_data.items():
            self._tickers_id[data['id']] = ticker
            self._markets_list.append(ticker)
        self.exchange = Exchanges.objects.get(name='poloniex')
        for item in tickers_data:
            pair = re.match(r'([a-zA-Z0-9]+)_([a-zA-Z0-9]+)', item)
            try:
                main_coin = ExchangeCoin.objects.get(exchange=self.exchange, symbol=pair.group(1))
                second_coin = ExchangeCoin.objects.get(exchange=self.exchange, symbol=pair.group(2))
                pair = Pair.objects.get(main_coin=main_coin, second_coin=second_coin)
                market = {tickers_data[item]['id']: pair.pk}
                self._tickers_list.update(market)
            except ExchangeCoin.DoesNotExist:
                pass
            except Pair.DoesNotExist:
                pass
        self._sub_thread = None
        self._event_loop = None
        self._last_seq_dic = {}
        self.order_books = OrderBooks()
        self.ticker_list = TickerList()

    def get_tickers(self):
        return self._tickers_list

    @staticmethod
    def _get_all_tickers():
        req = urllib.request.Request(GET_TICKERS_URL)
        with urllib.request.urlopen(req) as response:
            the_page = response.read()
        data = the_page.decode('utf8')
        data = json.loads(data)
        return data

    def start_subscribe(self):
        self._sub_thread = threading.Thread(target=self._start_subscriber)
        self._sub_thread.daemon = True
        self._sub_thread.start()

    def _start_subscriber(self):
        self._event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._event_loop)
        self._event_loop.run_until_complete(self._subscribe())

    async def _subscribe(self):
        async with websockets.connect(API_LINK) as websocket:
            await websocket.send(SUBSCRIBE_COMMAND.replace(
                '$', str(TICKER_SUBSCRIBE)))
            for ticker in self._markets_list:
                req = SUBSCRIBE_COMMAND.replace(
                    '$', '\"' + ticker + '\"')
                await websocket.send(req)

            # now parse received data
            while True:
                message = await websocket.recv()
                data = json.loads(message, object_pairs_hook=OrderedDict)
                if 'error' in data:
                    raise Exception('error arrived message={}'.format(message))

                if data[0] == 1010:
                    # this mean heartbeat
                    continue
                if len(data) < 2:
                    raise Exception(
                        'Short message arrived message={}'.format(message))
                if data[1] == 1:
                    # this mean the subscription is success
                    continue
                if data[1] == 0:
                    # this mean the subscription is failure
                    raise Exception(
                        'subscription failed message={}'.format(message))
                if data[0] == TICKER_SUBSCRIBE:
                    values = data[2]
                    ticker_id_int = values[0]
                    if ticker_id_int in self._tickers_list:
                        self.ticker_list.new_ticker(pair_id=self._tickers_list[ticker_id_int],
                                                    pair=self._tickers_id[ticker_id_int],
                                                    last=values[1],
                                                    date=time.time())
                        current_ticker = self.ticker_list.get_ticker_by_id(self._tickers_list[ticker_id_int])
                        if current_ticker.last is not None and current_ticker.prev_last is not None:
                            seconds = _D(current_ticker.date - current_ticker.prev_date)
                            if seconds > 1:
                                change = _D(current_ticker.last) - _D(current_ticker.prev_last)
                                rate_of_change = change / seconds
                                if abs(rate_of_change) >= settings.MIN_CHANGE_RATE_TO_REACT:
                                    market = self.order_books.get_market_by_name(self._tickers_id[ticker_id_int])
                                    if market is not None:
                                        # b = pickle.dumps(self.ticker_list)
                                        # bits = b.decode('cp1251')
                                        args_buy = {'pair': self._tickers_list[ticker_id_int],
                                                    'bids': market.bids[:100],
                                                    'change_rate': rate_of_change,
                                                    'ticker': jsonpickle.encode(self.ticker_list)}
                                        # args_sell = {'pair': self._tickers_list[ticker_id_int],
                                        #              'asks': market.asks[:100],
                                        #              'change_rate': rate_of_change,
                                        #              'ticker': bits}
                                        if rate_of_change > 0:
                                            res = start_calculate_poloniex_buy.delay(args_buy)
                                            print(res)
                                            # else:
                                            #     start_calculate_poloniex_sell.delay(
                                            #         json.dumps(args_sell, cls=DjangoJSONEncoder))
                                            # pair_temp = {'pair_id': pair.pk, 'last': ticker.last,
                                            #                      'percent': ticker.percent_change}
                                            # Group("trade").send({'text': json.dumps(pair_temp)})
                else:
                    ticker_id = self._tickers_id[data[0]]
                    seq = data[1]
                    for update in data[2]:
                        # this mean this is snapshot
                        if update[0] == 'i':
                            # UPDATE[1]['currencyPair'] is the ticker name
                            self._last_seq_dic[ticker_id] = seq
                            asks = []

                            for price, size in update[1]['orderBook'][0].items():
                                asks.append([price, size])

                            bids = []
                            for price, size in update[1]['orderBook'][1].items():
                                bids.append([price, size])

                            self.order_books.add_market(ticker_id=data[0], ticker_name=ticker_id, asks=asks, bids=bids)
                        # this mean add or change or remove
                        elif update[0] == 'o':
                            if self._last_seq_dic[ticker_id] + 1 != seq:
                                raise Exception('Problem with seq number prev_seq={},message={}'.format(
                                    self._last_seq_dic[ticker_id], message))

                            price = update[2]
                            side = 'bid' if update[1] == 1 else 'ask'
                            size = update[3]
                            # this mean remove
                            market = self.order_books.get_market_by_id(data[0])
                            if size == '0.00000000':
                                # print('\033[96mthis mean remove\033[0m')
                                if market is not None:
                                    market.remove_item(side=side, price=str(price))
                            # this mean add or change
                            else:
                                # print('\033[96mthis mean add or change\033[0m')
                                if market is not None:
                                    market.add_or_change(side=side, price=price, size=size)
                    self._last_seq_dic[ticker_id] = seq


class TickerList:
    def __init__(self):
        self.tickers = []

    def get_ticker_by_id(self, pair_id):
        for item in self.tickers:
            if item.pair_id == pair_id:
                return item
        return None

    def get_ticker_by_name(self, pair_name):
        for item in self.tickers:
            if item.pair == pair_name:
                return item
        return None

    def new_ticker(self, pair, pair_id, last, date):
        ticker = self.get_ticker_by_id(pair_id)
        if ticker is not None:
            ticker.prev_last = ticker.last
            ticker.prev_date = ticker.date
            ticker.last = last
            ticker.date = date
        else:
            new_ticker = Ticker(pair_id, pair, last, date)
            self.tickers.append(new_ticker)


class Ticker:
    def __init__(self, pair_id, pair, last, date):
        self.pair = pair
        self.pair_id = pair_id
        self.prev_last = None
        # self.prev_high = None
        # self.prev_low = None
        self.prev_date = None
        self.last = last
        # self.high = high
        # self.low = low
        self.date = date


class OrderBooks:
    def __init__(self):
        self.markets = []

    def add_market(self, ticker_id, ticker_name, asks, bids):
        market = self.get_market_by_id(ticker_id)
        if market is not None:
            market.bids = bids
            market.asks = asks
        else:
            new_market = MarketBook(ticker_id, ticker_name)
            new_market.asks = asks
            new_market.bids = bids
            self.markets.append(new_market)

    def get_market_by_id(self, ticker_id):
        for market in self.markets:
            if market.ticker_id == ticker_id:
                return market
        return None

    def get_market_by_name(self, ticker_name):
        for market in self.markets:
            if market.ticker_name == ticker_name:
                return market
        return None


class MarketBook:
    def __init__(self, ticker_id, ticker_name):
        self.ticker_name = ticker_name
        self.ticker_id = ticker_id
        self.bids = []
        self.asks = []

    def __repr__(self):
        return self.ticker_name

    def remove_item(self, side, price):
        if side == 'bid':
            for item in self.bids:
                if item[0] == price:
                    self.bids.remove(item)
                    # print('Удалил ' + str(self.ticker_name) + ' ' + str(side) + ' ' + str(price))
        elif side == 'ask':
            for item in self.asks:
                if item[0] == price:
                    self.asks.remove(item)
                    # print('Удалил ' + str(self.ticker_name) + ' ' + str(side) + ' ' + str(price))

    def add_or_change(self, side, price, size):
        # у bids обратная сортировка 10-9-8-7-...
        changed = False
        if side == 'bid':
            for item in self.bids:
                if item[0] == price:
                    item[1] = str(size)
                    changed = True
                    # print('изменил ' + str(self.ticker_name) + ' цена ' + str(price) + " кол-во " + str(size))
                    break
                elif item[0] < price:
                    self.bids.append([str(price), str(size)])
                    changed = True
                    self.bids.sort(reverse=True, key=lambda x: _D(x[0]))
                    # print('добавил ' + str(self.ticker_name) + ' цена ' + str(price) + " кол-во " + str(size))
                    break
            if not changed:
                self.bids.append([str(price), str(size)])
                self.bids.sort(reverse=True, key=lambda x: _D(x[0]))
                # print('добавил ' + str(self.ticker_name) + ' цена ' + str(price) + " кол-во " + str(size))
        # у asks прямая сортировка 7-8-9-10-...
        elif side == 'ask':
            for item in reversed(self.asks):
                if item[0] == price:
                    item[1] = str(size)
                    changed = True
                    # print('изменил ' + str(self.ticker_name) + ' цена ' + str(price) + " кол-во " + str(size))
                    break
                elif item[0] < price:
                    self.asks.append([str(price), str(size)])
                    changed = True
                    self.asks.sort(key=lambda x: _D(x[0]))
                    # print('добавил ' + str(self.ticker_name) + ' цена ' + str(price) + " кол-во " + str(size))
                    break
            if not changed:
                self.asks.append([str(price), str(size)])
                self.asks.sort(key=lambda x: _D(x[0]))
                # print('добавил ' + str(self.ticker_name) + ' цена ' + str(price) + " кол-во " + str(size))
