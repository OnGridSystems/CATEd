from __future__ import absolute_import, unicode_literals
import importlib
import jsonpickle
import time
import datetime
import re
from ccxt import ExchangeError
from celery.signals import worker_ready, celeryd_init
from django.db.models import Sum
from celery import shared_task, Task
from djangoTrade.celery import app
import requests
from trade.models import Exchanges, UserExchange, UserBalance
from tradeBOT.models import ExchangeCoin, Pair, ExchangeMainCoin, CoinMarketCupCoin, ExchangeTicker, Order, UserPair, \
    ToTrade, UserMainCoinPriority, UserCoinShare, UserOrder, Сalculations
from trade.tasks import pull_exchanges_balances
from django.conf import settings
from decimal import Decimal as _D
import asyncio
import time
import json
import threading
import urllib
import urllib.request
from collections import OrderedDict
import websockets
from celery.result import AsyncResult
from ccxt import CCXTError

GET_TICKERS_URL = 'https://poloniex.com/public?command=returnTicker'
API_LINK = 'wss://api2.poloniex.com'
SUBSCRIBE_COMMAND = '{"command":"subscribe","channel":$}'
TICKER_SUBSCRIBE = 1002
TICKER_OUTPUT = 'TICKER UPDATE {}={}(last),{}(lowestAsk),{}(highestBid),{}(percentChange),{}(baseVolume),{}(quoteVolume),{}(isFrozen),{}(high24hr),{}(low24hr)'
TRADE_OUTPUT = 'TRADE {}={}(tradeId),{}(bookSide),{}(price),{}(size),{}(timestamp)'


def class_for_name(module_name, class_name):
    m = importlib.import_module(module_name)
    c = getattr(m, class_name)
    return c


@shared_task
def pull_coinmarketcup():
    response = requests.get('https://api.coinmarketcap.com/v1/ticker/').json()
    if 'error' not in response:
        for item in response:
            try:
                old_coinmarket_coin = CoinMarketCupCoin.objects.get(coin_market_id=item['id'])
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


def round_down(x, s):
    x = int(x)
    return x - (x % (10 * s))


@shared_task
def rate_up_poloniex(args):
    pair = Pair.objects.get(pk=args['pair'])
    change_rate = _D(args['change_rate'])

    user_pairs = UserPair.objects.filter(pair=pair, rate_of_change__lte=change_rate,
                                         user_exchange__is_active_script=True,
                                         rate_of_change__gt=0,
                                         user_exchange__exchange__name__in=settings.TRADING_EXCHANGES)
    if len(user_pairs) > 0:
        for user_pair in user_pairs:
            print('Отправляю на покупку')
            calculate_order_for_user.delay(user_pair.pk, args, 'buy')
    return True


@shared_task
def rate_down_poloniex(args):
    pair = Pair.objects.get(pk=args['pair'])
    change_rate = _D(args['change_rate'])
    user_pairs = UserPair.objects.filter(pair=pair, rate_of_change__lte=abs(change_rate),
                                         user_exchange__is_active_script=True,
                                         user_exchange__exchange__name__in=settings.TRADING_EXCHANGES,
                                         rate_of_change__gt=0)
    print(user_pairs)
    for user_pair in user_pairs:
        print('Отправляю на продажу')
        calculate_order_for_user.delay(user_pair.pk, args, 'sell')


@shared_task
def calculate_order_for_user(user_pair_pk, params, type):
    try:
        user_pair = UserPair.objects.get(pk=user_pair_pk)
        change_rate = _D(params['change_rate'])
        if type == 'buy':
            print("Купить")
            bids = params['bids']
            ticker_list = jsonpickle.decode(params['ticker'])
            try:
                user_main_coin = UserMainCoinPriority.objects.get(main_coin__coin=user_pair.pair.main_coin,
                                                                  user_exchange=user_pair.user_exchange)
                main_coin_active = user_main_coin.is_active
            except UserMainCoinPriority.DoesNotExist:
                main_coin_active = True
            if main_coin_active:
                user_balance_second_coin = UserBalance.objects.get(ue=user_pair.user_exchange,
                                                                   coin=user_pair.pair.second_coin.symbol.lower())
                user_balance_second_coin_in_btc = user_balance_second_coin.btc_value
                user_second_coin_percent = user_balance_second_coin_in_btc / (
                    user_pair.user_exchange.total_btc / 100)
                user_coin_share = UserCoinShare.objects.get(user_exchange=user_pair.user_exchange,
                                                            coin=user_pair.pair.second_coin)
                user_need_second_coin_in_percent = user_coin_share.share
                user_nehvataen_in_percent_of_btc = user_need_second_coin_in_percent - user_second_coin_percent
                if user_nehvataen_in_percent_of_btc < 0.5:
                    return True
                # расчитываем приоритеты
                sum_priority_second_coin = UserPair.objects.filter(user_exchange=user_pair.user_exchange,
                                                                   pair__second_coin=user_pair.pair.second_coin).aggregate(
                    Sum('rank'))['rank__sum']
                user_need_to_buy_on_prior_in_percent_of_btc = _D(user_nehvataen_in_percent_of_btc) * (
                    _D(user_pair.rank) / _D(sum_priority_second_coin))

                user_need_to_buy_on_prior_in_btc = (user_pair.user_exchange.total_btc / 100) * \
                                                   user_need_to_buy_on_prior_in_percent_of_btc
                print('Надо взять в BTC: {}'.format(user_need_to_buy_on_prior_in_btc))
                user_need_to_buy_on_prior_in_first_coin = 0

                # сколько нужно взять в первой валюте
                if user_pair.pair.main_coin.symbol.upper() == 'BTC':
                    user_need_to_buy_on_prior_in_first_coin = user_need_to_buy_on_prior_in_btc
                else:
                    ticker = ticker_list.get_ticker_by_name('BTC_' + user_pair.pair.main_coin.symbol.upper())
                    if ticker is not None:
                        user_need_to_buy_on_prior_in_first_coin = _D(user_need_to_buy_on_prior_in_btc) / _D(ticker.last)
                    else:
                        ticker = ticker_list.get_ticker_by_name(user_pair.pair.main_coin.symbol.upper() + '_BTC')
                        if ticker is not None:
                            user_need_to_buy_on_prior_in_first_coin = _D(user_need_to_buy_on_prior_in_btc) * _D(
                                ticker.last)
                        else:
                            print('ИДИТЕ НАЗУЙ С МОНЕТОЙ: ' + str(user_pair.pair.main_coin))
                            return True
                print('Нужно взять в {}: {}'.format(user_pair.pair.main_coin.symbol.upper(),
                                                    user_need_to_buy_on_prior_in_first_coin))

                # надо потратить первой валюты user_need_to_buy_on_prior_in_first_coin
                try:
                    user_balance_main_coin = UserBalance.objects.get(ue=user_pair.user_exchange,
                                                                     coin=user_pair.pair.main_coin.symbol.lower())
                    if user_balance_main_coin.free == 0 or user_balance_main_coin.free < 0.0001:
                        print('{} доступно {}'.format(user_pair.pair.main_coin.symbol.upper(),
                                                      user_balance_main_coin.free))
                        return True
                    if user_balance_main_coin.free < user_need_to_buy_on_prior_in_first_coin:
                        user_need_to_buy_on_prior_in_first_coin = user_balance_main_coin.free
                except UserBalance.DoesNotExist:
                    print('Не нашел такой валюты у пользователя')
                    return True
                price = calculate_price(user_need_to_buy_on_prior_in_first_coin, o_type='buy', bids=bids)
                total = user_need_to_buy_on_prior_in_first_coin / price
                if user_need_to_buy_on_prior_in_first_coin < 0.0001:
                    return True
                print('Хочу потратить {} {} чтобы купить {} {}'.format(user_need_to_buy_on_prior_in_first_coin,
                                                                       user_pair.pair.main_coin.symbol.upper(),
                                                                       total,
                                                                       user_pair.pair.second_coin.symbol.upper()))
                print('Считал по {}'.format(price))

                calculations = Сalculations()
                calculations.user_pair = user_pair
                calculations.rate_change = change_rate
                calculations.type = type
                calculations.depth_coef = settings.DEPTH_COEFFICIENT
                calculations.price = price
                calculations.amount = total
                calculations.bids = json.dumps(bids)
                calculations.asks = None
                calculations.save()

                try:
                    to_trade = ToTrade.objects.get(user_pair=user_pair, type='buy')
                    to_trade.price = price
                    to_trade.amount = total
                    to_trade.total = user_need_to_buy_on_prior_in_first_coin
                    to_trade.total_f = user_need_to_buy_on_prior_in_first_coin - (
                        user_need_to_buy_on_prior_in_first_coin * _D('.0015'))
                    to_trade.percent_react = change_rate
                    to_trade.save()
                except ToTrade.DoesNotExist:
                    new_order = ToTrade()
                    new_order.user_pair = user_pair
                    new_order.type = 'buy'
                    new_order.percent_react = change_rate
                    new_order.price = price
                    new_order.amount = total
                    new_order.total = user_need_to_buy_on_prior_in_first_coin
                    new_order.total_f = user_need_to_buy_on_prior_in_first_coin - (
                        user_need_to_buy_on_prior_in_first_coin * _D('.0015'))
                    new_order.fee = _D('.0015')
                    new_order.cause = 'Change rate'
                    new_order.save()
        elif type == 'sell':
            print('Продать')
            asks = params['asks']
            user_have_second_coin = UserBalance.objects.get(ue=user_pair.user_exchange,
                                                            coin=user_pair.pair.second_coin.symbol.lower())
            if user_have_second_coin.free > 0.001:
                price = calculate_price(amount=user_have_second_coin.free, o_type='sell', asks=asks)
                total = user_have_second_coin.free * _D(price)
                print('Нашел цену: ' + str(price))
                print('Хочу потратить {} {} чтобы купить {} {}'.format(user_have_second_coin.free,
                                                                       user_pair.pair.second_coin.symbol.upper(),
                                                                       total,
                                                                       user_pair.pair.main_coin.symbol.upper()))

                calculations = Сalculations()
                calculations.user_pair = user_pair
                calculations.rate_change = change_rate
                calculations.type = type
                calculations.depth_coef = settings.DEPTH_COEFFICIENT
                calculations.price = price
                calculations.amount = user_have_second_coin.free
                calculations.asks = json.dumps(asks)
                calculations.bids = None
                calculations.save()

                try:
                    to_trade = ToTrade.objects.get(user_pair=user_pair, type='sell')
                    to_trade.price = price
                    to_trade.amount = user_have_second_coin.free
                    to_trade.total = total
                    to_trade.total_f = total - (total * _D('.0015'))
                    to_trade.percent_react = change_rate
                    to_trade.save()
                except ToTrade.DoesNotExist:
                    new_order = ToTrade()
                    new_order.user_pair = user_pair
                    new_order.type = 'sell'
                    new_order.percent_react = change_rate
                    new_order.price = price
                    new_order.amount = user_have_second_coin.free
                    new_order.total = total
                    new_order.total_f = total - (total * _D('.0015'))
                    new_order.fee = _D('.0015')
                    new_order.cause = 'Change rate'
                    new_order.save()
    except UserPair.DoesNotExist:
        pass
    return True


def calculate_price(amount=0, o_type=None, bids=None, asks=None):
    if amount == 0:
        return 0
    if o_type == 'buy' and bids is None:
        raise BidsAsksTypeException('Отсутствует стакан для покупки')
    if o_type == 'sell' and asks is None:
        raise BidsAsksTypeException('Отсутствует стакан для продажи')

    depth = _D(settings.DEPTH_COEFFICIENT) * _D(amount)

    if o_type == 'buy':
        bids = calculate_full_order_book(bids)
        sum_t = _D(0)
        for i in range(len(bids)):
            sum_t += _D(bids[i][2])
            if sum_t > depth:
                return _D(bids[i][0]) + _D('.00000001')
    elif o_type == 'sell':
        asks = calculate_full_order_book(asks)
        sum_t = _D(0)
        for i in range(len(asks)):
            sum_t += _D(asks[i][2])
            if sum_t > depth:
                return _D(asks[i][0]) - _D('.00000001')


class BidsAsksTypeException(Exception):
    def __init__(self, value):
        self.value = value


    def __str__(self):
        return repr(self.value)


def calculate_full_order_book(book):
    for item in book:
        item.append(str(_D(item[0]) * _D(item[1])))
    return book


class WampTickerPoloniex(Task):
    ignore_result = False

    def run(self, *args, **kwargs):
        sub = PoloniexSubscriber()
        sub.start_subscribe()
        try:
            while True:
                pass
        except KeyboardInterrupt:
            # quit
            pass


WampTickerPoloniex = app.register_task(WampTickerPoloniex())


@celeryd_init.connect(sender='worker_high@lab-sk')
def start_ticker(**kwargs):
    WampTickerPoloniex.apply_async(queue='high')
    SetOrderTask.apply_async(queue='set_orders')

class PoloniexSubscriber(object):
    def __init__(self):
        self.workers = {}
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

    def check_task_status(self, task_id):
        return AsyncResult(task_id).ready()

    def check_pair_task_status(self, pair_id):
        if pair_id in self.workers:
            return self.check_task_status(self.workers[pair_id])
        else:
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
                                        is_task_ready = self.check_pair_task_status(self._tickers_list[ticker_id_int])
                                        if rate_of_change > 0:
                                            if is_task_ready:
                                                args_buy = {'pair': self._tickers_list[ticker_id_int],
                                                            'bids': market.bids[:100],
                                                            'change_rate': rate_of_change,
                                                            'ticker': jsonpickle.encode(self.ticker_list)}
                                                wor = rate_up_poloniex.delay(args_buy)
                                                self.workers.update({self._tickers_list[ticker_id_int]: wor.task_id})
                                        else:
                                            if is_task_ready:
                                                args_sell = {'pair': self._tickers_list[ticker_id_int],
                                                             'asks': market.asks[:100],
                                                             'change_rate': rate_of_change}

                                                wor = rate_down_poloniex.delay(args_sell)
                                                self.workers.update({self._tickers_list[ticker_id_int]: wor.task_id})
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


class CheckSetOrderTask(Task):
    ignore_result = False

    def run(self, *args, **kwargs):
        task = pull_exchanges_balances.delay()
        while not AsyncResult(task.task_id).ready():
            pass
        try:
            user_orders = UserOrder.objects.filter(date_cancel=None)
            orders_to_close = user_orders.filter(
                date_created__lte=datetime.datetime.now() - datetime.timedelta(minutes=settings.ORDER_TTL))
            print('Ордера пользователей {}'.format(user_orders))
            print('Ордера к закрытию {}'.format(orders_to_close))
            for uo in user_orders:
                exchange_object = class_for_name('ccxt', uo.ue.exchange.name)({
                    'apiKey': uo.ue.apikey,
                    'secret': uo.ue.apisecret
                })
                try:
                    order_status = exchange_object.fetch_order_status(str(uo.order_number))
                except CCXTError as er:
                    continue
                if order_status == 'open':
                    if uo in orders_to_close:
                        print('Ордер № {} пора закрыть, его время пришло'.format(uo.order_number))
                        try:
                            print('Пытаюсь отменить ордер № {}'.format(uo.order_number))
                            canc = exchange_object.cancel_order(str(uo.order_number))
                            if canc['success'] == 1:
                                uo.date_cancel = datetime.datetime.now()
                                uo.cancel_desc = 'TTL'
                                uo.save()
                        except CCXTError as er:
                            print('При отмене ордера № {} возникла ошибка: {}'.format(uo.order_number, er))
                            continue
                    else:
                        try:
                            current_balance_main_coin = UserBalance.objects.get(ue=uo.ue,
                                                                                coin=uo.pair.main_coin.symbol.lower())
                            uo.interim_main_coin = current_balance_main_coin.total
                            uo.save()
                        except UserBalance.DoesNotExist:
                            pass
                elif order_status == 'closed':
                    print('Ордер № {} закрыт'.format(uo.order_number))
                    uo.date_cancel = datetime.datetime.now()
                    try:
                        current_balance_main_coin = UserBalance.objects.get(ue=uo.ue,
                                                                            coin=uo.pair.main_coin.symbol.lower())
                        uo.main_coin_after_total = current_balance_main_coin.total
                        uo.main_coin_after_free = current_balance_main_coin.free
                        uo.main_coin_after_used = current_balance_main_coin.used
                    except UserBalance.DoesNotExist:
                        uo.main_coin_after_total = '-1'
                        uo.main_coin_after_used = '-1'
                        uo.main_coin_after_free = '-1'
                    try:
                        current_balance_second_coin = UserBalance.objects.get(ue=uo.ue,
                                                                              coin=uo.pair.second_coin.symbol.lower())
                        uo.second_coin_after_total = current_balance_second_coin.total
                        uo.second_coin_after_used = current_balance_second_coin.used
                        uo.second_coin_after_free = current_balance_second_coin.free
                    except UserBalance.DoesNotExist:
                        uo.second_coin_after_total = '-1'
                        uo.second_coin_after_used = '-1'
                        uo.second_coin_after_free = '-1'
                    if uo.order_type == 'buy':
                        fact_total = _D(uo.interim_main_coin) - _D(current_balance_main_coin.total)
                        uo.fact_total = fact_total
                        if fact_total != 0:
                            fact_fee = 100 * _D(uo.total) / _D(fact_total) - 100
                            uo.fact_fee = fact_fee
                            if fact_fee > 0.2:
                                uo.is_ok = False
                    elif uo.order_type == 'sell':
                        fact_total = _D(current_balance_main_coin.total) - _D(uo.interim_main_coin)
                        uo.fact_total = fact_total
                        if fact_total != 0:
                            fact_fee = 100 * _D(uo.total) / _D(fact_total) - 100
                            uo.fact_fee = fact_fee
                            if fact_fee > 0.2:
                                uo.is_ok = False
                    uo.cancel_desc = 'Worked'
                    uo.save()
        except CCXTError:
            pass
        except Exception as e:
            print('При проверке ордера возникла ошибка: {}'.format(e))
            pass
        try:
            to_trade = ToTrade.objects.filter(
                date_updated__gte=datetime.datetime.now() - datetime.timedelta(minutes=5)).earliest('date_created')

            already_in_orders = UserOrder.objects.filter(ue=to_trade.user_pair.user_exchange,
                                                         pair=to_trade.user_pair.pair, date_cancel=None)
            if len(already_in_orders) > 0:
                to_trade.delete()
            else:
                exchange_name = to_trade.user_pair.user_exchange.exchange.name
                exchange_object = class_for_name('ccxt', exchange_name)({
                    'apiKey': to_trade.user_pair.user_exchange.apikey,
                    'secret': to_trade.user_pair.user_exchange.apisecret
                })
                user_balance_main_coin = UserBalance.objects.get(ue=to_trade.user_pair.user_exchange,
                                                                 coin=to_trade.user_pair.pair.main_coin.symbol)
                user_balance_second_coin = UserBalance.objects.get(ue=to_trade.user_pair.user_exchange,
                                                                   coin=to_trade.user_pair.pair.second_coin.symbol)
                order = None
                try:
                    if to_trade.type == 'buy':
                        order = exchange_object.create_limit_buy_order(
                            symbol=to_trade.user_pair.pair.second_coin.symbol.upper() + '/' + to_trade.user_pair.pair.main_coin.symbol.upper(),
                            amount=to_trade.amount,
                            price=to_trade.price,
                            params={'postOnly': 1}
                        )
                        print('Ответ от биржи (покупка): {}'.format(order))
                    elif to_trade.type == 'sell':
                        order = exchange_object.create_limit_sell_order(
                            symbol=to_trade.user_pair.pair.second_coin.symbol.upper() + '/' + to_trade.user_pair.pair.main_coin.symbol.upper(),
                            amount=to_trade.amount,
                            price=to_trade.price,
                            params={'postOnly': 1}
                        )
                        print('Ответ от биржи (продажа): {}'.format(order))
                    if order is not None:
                        pull_exchanges_balances.delay(to_trade.user_pair.user_exchange.pk)
                        user_order = UserOrder()
                        user_order.ue = to_trade.user_pair.user_exchange
                        user_order.pair = to_trade.user_pair.pair
                        user_order.order_type = to_trade.type
                        user_order.order_number = order['id']
                        user_order.first_coin_before = user_balance_main_coin.total
                        user_order.second_coin_before = user_balance_second_coin.total
                        user_order.price = to_trade.price
                        user_order.amount = to_trade.amount
                        user_order.total = to_trade.price * to_trade.amount
                        user_order.fee = _D('0.0015')
                        user_order.save()
                    else:
                        pass
                except ExchangeError:
                    pass
                to_trade.delete()
        except ToTrade.DoesNotExist:
            time.sleep(5)
        except UserBalance.DoesNotExist:
            time.sleep(2)
            pass
        SetOrderTask.apply_async(queue='set_orders')
        return True


SetOrderTask = app.register_task(CheckSetOrderTask())

