from __future__ import absolute_import, unicode_literals
import asyncio
import time
import json
import re
import threading
import urllib
import urllib.request
from collections import OrderedDict
import sys
import datetime
import websockets
from django.core.management.base import BaseCommand

from django.conf import settings
import jsonpickle

from decimal import Decimal as _D
import warnings

warnings.filterwarnings(
    'ignore', r"DateTimeField .* received a naive datetime",
    RuntimeWarning, r'django\.db\.models\.fields')

GET_TICKERS_URL = 'https://poloniex.com/public?command=returnTicker'
API_LINK = 'wss://api2.poloniex.com'
SUBSCRIBE_COMMAND = '{"command":"subscribe","channel":$}'
TICKER_SUBSCRIBE = 1002
TICKER_OUTPUT = 'TICKER UPDATE: last {}, low {}, high {}, date {}'
TRADE_OUTPUT = 'TRADE {}={}(tradeId),{}(bookSide),{}(price),{}(size),{}(timestamp)'

DIRECTIONS_COUNT = 7
UNIDIRECTION_COUNT = 4


class PoloniexSubscriber(object):
    def __init__(self):
        self._tickers_list = {}
        self._markets_list = []
        self._tickers_id = {}
        tickers_data = self._get_all_tickers()
        for ticker, data in tickers_data.items():
            self._tickers_id[data['id']] = ticker
            self._markets_list.append(ticker)
        self._sub_thread = None
        self._event_loop = None
        self._last_seq_dic = {}
        self.order_books = OrderBooks()
        self.ticker_list = TickerList()
        self.directions = {}
        self.extremums = {}

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

    def add_market_direction(self, pair_id, direction, timestamp):
        if pair_id in self.directions:
            if len(self.directions[pair_id]) >= DIRECTIONS_COUNT:
                self.directions[pair_id].pop(0)
            self.directions[pair_id].append([direction, timestamp])
        else:
            self.directions.update({pair_id: [[direction, timestamp]]})

    def check_directions_is_extremum(self, pair_id):
        if pair_id in self.directions:
            if len(self.directions[pair_id]) < DIRECTIONS_COUNT:
                return False
            else:
                sum_first_n_elem = sum([x[0] for x in self.directions[pair_id][:UNIDIRECTION_COUNT]])
                sum_last_n_elem = sum([x[0] for x in self.directions[pair_id][UNIDIRECTION_COUNT:]])
                if sum_first_n_elem >= UNIDIRECTION_COUNT - 1 and sum_last_n_elem == 0:
                    return 'upper'
                elif sum_first_n_elem <= 1 and sum_last_n_elem == DIRECTIONS_COUNT - UNIDIRECTION_COUNT:
                    return 'lower'
                else:
                    return False
        else:
            return False

    def check_extremum(self, pair_id, date, ext_type, last):
        if pair_id in self.extremums:
            if ext_type == self.extremums[pair_id][1]:
                return False
            else:
                if self.extremums[pair_id][1] == 'upper':
                    if self.extremums[pair_id][2] < last:
                        return False
                    else:
                        self.extremums.update({pair_id: [date, ext_type, last]})
                        return True
                elif self.extremums[pair_id][1] == 'lower':
                    if self.extremums[pair_id][2] > last:
                        return False
                    else:
                        self.extremums.update({pair_id: [date, ext_type, last]})
                        return True
        else:
            self.extremums.update({pair_id: [date, ext_type, last]})
            return True

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
                try:
                    message = await websocket.recv()
                except websockets.ConnectionClosed:
                    print('Connection was closed, reconnect')
                    self._sub_thread.join()
                    time.sleep(10)
                    self.__init__()
                    self.start_subscribe()
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
                    # print(values)
                    ticker_id_int = values[0]
                    self.ticker_list.new_ticker(pair_id=self._tickers_id[ticker_id_int],
                                                pair=self._tickers_id[ticker_id_int],
                                                last=values[1],
                                                high=values[3],
                                                low=values[2],
                                                date=time.time())
                    # if 'BTC_BCH' == self._tickers_id[ticker_id_int]:
                    ct = self.ticker_list.get_ticker_by_id(self._tickers_id[ticker_id_int])
                    # print(TICKER_OUTPUT.format(ct.pair, ct.last, ct.low, ct.high, ct.date))
                    if ct.last is not None and ct.prev_last is not None:
                        new_direction = False
                        if ct.low > ct.prev_low and ct.high > ct.prev_high:
                            self.add_market_direction(ct.pair, 1, ct.date)
                            new_direction = True
                            with open(ct.pair + '.txt', 'a') as pair_file:
                                pair_file.write(
                                    '1, date: {}, last: {} \n'.format(datetime.datetime.fromtimestamp(ct.date),
                                                                      ct.last))
                        elif ct.low < ct.prev_low and ct.high < ct.prev_high:
                            self.add_market_direction(ct.pair, 0, ct.date)
                            new_direction = True
                            with open(ct.pair + '.txt', 'a') as pair_file:
                                pair_file.write(
                                    '0, date: {}, last: {} \n'.format(datetime.datetime.fromtimestamp(ct.date),
                                                                      ct.last))
                        if new_direction:
                            extremum = self.check_directions_is_extremum(ct.pair)
                            if extremum is not False:
                                is_ext = self.check_extremum(ct.pair, ct.date, extremum, ct.last)
                                if is_ext:
                                    with open('extremums.txt', 'a') as file:
                                        file.write(
                                            'Пара {} найден {}, дата {} \n'.format(ct.pair, extremum,
                                                                                   datetime.datetime.now()))
                                    print('Пара {} найден {}, дата {}'.format(ct.pair, extremum, datetime.datetime.now()))

                                #
                                #     seconds = _D(current_ticker.date - current_ticker.prev_date)
                                #     if seconds > 1:
                                #         change = _D(current_ticker.last) - _D(current_ticker.prev_last)
                                #         rate_of_change = change / seconds
                                # if abs(rate_of_change) >= settings.MIN_CHANGE_RATE_TO_REACT:
                                #     market = self.order_books.get_market_by_name(self._tickers_id[ticker_id_int])
                                #     if market is not None:
                                # b = pickle.dumps(self.ticker_list)
                                # bits = b.decode('cp1251')
                                # args_buy = {'pair': self._tickers_list[ticker_id_int],
                                #             'bids': market.bids[:100],
                                #             'change_rate': rate_of_change,
                                #             'ticker': jsonpickle.encode(self.ticker_list)}
                                # args_sell = {'pair': self._tickers_list[ticker_id_int],
                                #              'asks': market.asks[:100],
                                #              'change_rate': rate_of_change,
                                #              'ticker': bits}
                                # if rate_of_change > 0:
                                #     pass
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

    def new_ticker(self, pair, pair_id, last, high, low, date):
        ticker = self.get_ticker_by_id(pair_id)
        if ticker is not None:
            ticker.prev_last = ticker.last
            ticker.prev_date = ticker.date
            ticker.prev_high = ticker.high
            ticker.prev_low = ticker.low
            ticker.last = last
            ticker.date = date
            ticker.high = high
            ticker.low = low
        else:
            new_ticker = Ticker(pair_id, pair, last, high, low, date)
            self.tickers.append(new_ticker)


class Ticker:
    def __init__(self, pair_id, pair, last, high, low, date):
        self.pair = pair
        self.pair_id = pair_id
        self.prev_last = None
        self.prev_high = None
        self.prev_low = None
        self.prev_date = None
        self.last = last
        self.high = high
        self.low = low
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


if __name__ == '__main__':
    """ Do your work here """
    sub = PoloniexSubscriber()
    sub.start_subscribe()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        # quit
        pass
