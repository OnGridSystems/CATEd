# coding=utf-8
from trade.drivers import btce_driver


class BtceTrader:
    def __init__(self, secret=None, key=None):
        self.api_key_secret = {
            'Key': key,
            'Secret': secret,
        }
        self.public_api = btce_driver.PublicAPIv3()
        self.trade_api = btce_driver.TradeAPIv1(self.api_key_secret)
        self.coins = []
        self.markets = []
        self.exchanges = []

    def pull_exchanges(self):
        if len(self.exchanges) > 0:
            raise Exception('Пары начитаны')
        else:
            print('Начитываю пары')
            exchanges = self.public_api.call('info')
            for e in exchanges['pairs']:
                exch = Exchange(e)
                exch_info = self.public_api.call('ticker', e)
                exch_his = self.public_api.call('trades', e)
                for eh in exch_his[e]:
                    history = ExchangeHistory(tid=eh['tid'])
                    history.price = eh['price']
                    history.type = 'sell' if eh['type'] == 'ask' else 'buy'
                    history.amount = eh['amount']
                    history.timestamp = eh['timestamp']
                    exch.history.append(history)
                exch.high = exch_info[e]['high']
                exch.low = exch_info[e]['low']
                exch.last = exch_info[e]['last']
                exch.buy = exch_info[e]['buy']
                exch.sell = exch_info[e]['sell']
                exch.fee = exchanges['pairs'][e]['fee']
                exch.min_amount = exchanges['pairs'][e]['min_amount']
                exch.min_price = exchanges['pairs'][e]['min_price']

                self.exchanges.append(exch)

    def pull_balances(self):
        balances = self.trade_api.call('getInfo')
        return balances

    def pull_orders(self):
        orders = self.trade_api.call('ActiveOrders')
        return orders

    def sell(self, pair, rate, amount):
        sell = self.trade_api.call('Trade', type='sell', pair=pair, rate=rate, amount=amount)
        if sell['success'] != '1':
            raise Exception('Не удалось установить ордер на продажу')

    def buy(self, pair, rate, amount):
        buy = self.trade_api.call('Trade', type='buy', pair=pair, rate=rate, amount=amount)
        if buy['success'] != '1':
            raise Exception('Не удалось установить ордер на покупку')


class Exchange(object):
    def __init__(self, name=None):
        self.name = name
        self.fee = None
        self.min_amount = None
        self.min_price = None
        self.high = None
        self.low = None
        self.last = None
        self.buy = None
        self.sell = None
        self.history = []
        self.orders = []

    def __repr__(self):
        return '<' + self.name + '>'


class ExchangeHistory(object):
    def __init__(self, tid=None):
        self.tid = tid
        self.timestamp = None
        self.amount = None
        self.price = None
        self.type = None

    def __repr__(self):
        return '<' + self.type + ' - ' + str(self.price) + '>'


class ExchangeOrders(object):
    def __init__(self, tid=None):
        self.tid = tid
        self.type = None
        self.amount = None
        self.rate = None
        self.timestamp_created = None


class Coin(object):
    def __init__(self, name=None, balance=None):
        self.name = name
        self.balance = balance

    def __repr__(self):
        return '<' + self.name + ': ' + str(self.balance) + '>'
