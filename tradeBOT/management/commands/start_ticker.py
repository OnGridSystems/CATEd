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
from trade.models import Exchanges
from tradeBOT.models import ExchangeCoin, Pair, ExchangeTicker, UserPair, UserMainCoinPriority
from decimal import Decimal
import warnings

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
        tickers_data = self._get_all_tickers()
        self.exchange = Exchanges.objects.get(exchange='poloniex')
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
                        pair = Pair.objects.get(pk=self._tickers_list[ticker_id_int])
                        need_calculate = False
                        try:
                            last_pair_ticker = ExchangeTicker.objects.filter(pair=pair,
                                                                             date_time__gte=datetime.datetime.fromtimestamp(
                                                                                 time.time() - 10)).latest('date_time')
                            need_calculate = True
                        except ExchangeTicker.DoesNotExist:
                            pass
                        ticker = ExchangeTicker()
                        ticker.exchange = self.exchange
                        ticker.pair = pair
                        ticker.high = values[8]
                        ticker.low = values[9]
                        ticker.last = values[1]
                        ticker.bid = values[3]
                        ticker.ask = values[2]
                        ticker.base_volume = values[5]
                        ticker.percent_change = values[4]
                        ticker.save()
                        if need_calculate and last_pair_ticker:
                            thread = threading.Thread(target=calculate_to_trade, args=(last_pair_ticker, ticker))
                            thread.daemon = True
                            thread.start()
                            # pair_temp = {'pair_id': pair.pk, 'last': ticker.last,
                            #                      'percent': ticker.percent_change}
                            # Group("trade").send({'text': json.dumps(pair_temp)})


def calculate_to_trade(last_ticker, new_ticker):
    seconds = Decimal(str(int((new_ticker.date_time - last_ticker.date_time).total_seconds())))
    if seconds > 1:
        change = Decimal(str(new_ticker.last)) - Decimal(str(last_ticker.last))
        rate_of_change = change / seconds
        user_pairs = UserPair.objects.filter(pair=last_ticker.pair, rate_of_change__lte=abs(rate_of_change),
                                             user_exchange__is_active_script=True).order_by('-rank')
        if len(user_pairs) > 0:
            for user_pair in user_pairs:
                try:
                    user_main_coin = UserMainCoinPriority.objects.get(main_coin__coin=user_pair.pair.main_coin,
                                                                      user_exchange=user_pair.user_exchangem)
                    main_coin_active = user_main_coin.is_active
                except UserMainCoinPriority.DoesNotExist:
                    main_coin_active = True
                if main_coin_active:
                    print('Change rate: ' + str(rate_of_change))
                    print(
                        'Pair: ' + str(user_pair.pair.main_coin.symbol) + '-' + str(user_pair.pair.second_coin.symbol))
    return
