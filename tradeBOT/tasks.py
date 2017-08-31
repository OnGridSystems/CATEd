from __future__ import absolute_import, unicode_literals
import json
import re
from django.db.models import Q, Sum
from http.client import HTTPException
from decimal import Decimal as D, getcontext, setcontext, Context, localcontext
from celery.schedules import crontab
from celery.task import periodic_task
import datetime
from celery import shared_task
import requests
from trade.models import Exchanges, UserExchange, UserBalance
from tradeBOT.models import ExchangeCoin, Pair, ExchangeMainCoin, CoinMarketCupCoin, ExchangeTicker, Order, UserPair, \
    ToTrade, UserMainCoinPriority, UserCoinShare, UserOrder
from django.conf import settings
from decimal import Decimal as _D
from trade.tasks import pull_user_balances


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


# @shared_task
# def pull_poloniex_orders():
#     getcontext().rounding = 'ROUND_DOWN'
#     exchange = Exchanges.objects.get(exchange='poloniex')
#     poloniex_ue = UserExchanges.objects.filter(pk=4)
#     if len(poloniex_ue) > 0:
#         for ue in poloniex_ue:
#             try:
#                 ue_apisecret = ue.apisecret.encode()
#                 driver = Poloniex(secret=ue_apisecret, apikey=ue.apikey)
#                 orders = driver.returnTradeHistory(start=1, end=9999999999)
#                 total_naeb = {}
#                 for item in orders:
#                     pair = re.match(r'([a-zA-Z0-9]+)_([a-zA-Z0-9]+)', item)
#                     total_naeb[pair.group(1)] = 0
#                     for order in orders[item]:
#                         try:
#                             e_order = Order.objects.get(orderNumber=order['tradeID'])
#                         except Order.DoesNotExist:
#                             n_order = Order()
#                             n_order.ue = ue
#                             n_order.pair = item
#                             n_order.globalTradeID = order['globalTradeID']
#                             n_order.type = order['type']
#                             n_order.total = order['total']
#                             n_order.amount = order['amount']
#                             n_order.tradeID = order['tradeID']
#                             n_order.date_time = order['date']
#                             n_order.category = order['category']
#                             n_order.orderNumber = order['orderNumber']
#                             n_order.fee = order['fee']
#                             n_order.rate = order['rate']
#                             total = (D(order['rate']) * D(order['amount'])).quantize(D('.000000001'))
#                             if total.quantize(D('.00000001')) != D(str(order['total'])):
#                                 total = round(float(total), 8)
#                             n_order.our_total = total
#                             n_order.save()
#             except HTTPException:
#                 print('Ошибка, начинаем заново')
#     else:
#         pass
#     return True


# @shared_task
# def calculate_to_trade():
#     pass
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


# @shared_task
# def start_calculate_poloniex_buy(args):
#     data = json.loads(args)
#     pair = Pair.objects.get(pk=data['pair'])
#     print(pair.main_coin.symbol.upper() + '_' + pair.second_coin.symbol.upper())
#     bids = data['bids']
#     change_rate = _D(data['change_rate'])
#     print('Пара {}'.format(pair.main_coin.symbol.upper() + '_' + pair.second_coin.symbol.upper()))
#     print("Коэфициент цены: {}".format(change_rate))
#
#     user_pairs = UserPair.objects.filter(pair=pair, rate_of_change__lte=change_rate,
#                                          user_exchange__is_active_script=True,
#                                          user_exchange__exchange__exchange='poloniex', rate_of_change__gt=0)
#     print(user_pairs)
#     if len(user_pairs) > 0:
#         for user_pair in user_pairs:
#             try:
#                 user_main_coin = UserMainCoinPriority.objects.get(main_coin__coin=user_pair.pair.main_coin,
#                                                                   user_exchange=user_pair.user_exchange)
#                 main_coin_active = user_main_coin.is_active
#             except UserMainCoinPriority.DoesNotExist:
#                 main_coin_active = True
#             if main_coin_active:
#                 user_balance_second_coin = UserBalance.objects.get(ue=user_pair.user_exchange,
#                                                                    coin=user_pair.pair.second_coin.symbol.lower())
#                 user_balance_second_coin_in_btc = user_balance_second_coin.btc_value
#                 user_second_coin_percent = user_balance_second_coin_in_btc / (
#                     user_pair.user_exchange.total_btc / 100)
#                 user_coin_share = UserCoinShare.objects.get(user_exchange=user_pair.user_exchange,
#                                                             coin=user_pair.pair.second_coin)
#                 user_need_second_coin_in_percent = user_coin_share.share
#                 user_nehvataen_in_percent_of_btc = user_need_second_coin_in_percent - user_second_coin_percent
#
#                 # расчитываем приоритеты
#                 sum_priority_second_coin = UserPair.objects.filter(user_exchange=user_pair.user_exchange,
#                                                                    pair__second_coin=user_pair.pair.second_coin).aggregate(
#                     Sum('rank'))['rank__sum']
#                 user_need_to_buy_on_prior_in_percent_of_btc = _D(user_nehvataen_in_percent_of_btc) * (
#                     _D(user_pair.rank) / _D(sum_priority_second_coin))
#
#                 user_need_to_buy_on_prior_in_btc = (user_pair.user_exchange.total_btc / 100) * \
#                                                    user_need_to_buy_on_prior_in_percent_of_btc
#                 print('Надо взять в BTC: {}'.format(user_need_to_buy_on_prior_in_btc))
#                 user_need_to_buy_on_prior_in_first_coin = 0
#
#                 # сколько нужно взять в первой валюте
#
#                 if user_pair.pair.main_coin.symbol.upper() == 'BTC':
#                     user_need_to_buy_on_prior_in_first_coin = user_need_to_buy_on_prior_in_btc
#                 else:
#                     try:
#                         last_price = ExchangeTicker.objects.filter(pair__main_coin__symbol='BTC',
#                                                                    pair__second_coin=user_pair.pair.main_coin).latest(
#                             'date_time')
#                         user_need_to_buy_on_prior_in_first_coin = _D(user_need_to_buy_on_prior_in_btc) / _D(
#                             last_price.last)
#                     except ExchangeTicker.DoesNotExist:
#                         try:
#                             last_price = ExchangeTicker.objects.filter(pair__second_coin__symbol='BTC',
#                                                                        pair__main_coin=user_pair.pair.main_coin).latest(
#                                 'date_time')
#                             user_need_to_buy_on_prior_in_first_coin = _D(
#                                 user_need_to_buy_on_prior_in_btc) * _D(last_price.last)
#                         except ExchangeTicker.DoesNotExist:
#                             print('ИДИТЕ НАЗУЙ С МОНЕТОЙ: ' + str(user_pair.pair.main_coin))
#                 print('Нужно взять в {}: {}'.format(user_pair.pair.main_coin.symbol.upper(),
#                                                     user_need_to_buy_on_prior_in_first_coin))
#
#                 # надо потратить первой валюты user_need_to_buy_on_prior_in_first_coin
#                 try:
#                     user_balance_main_coin = UserBalance.objects.get(ue=user_pair.user_exchange,
#                                                                      coin=user_pair.pair.main_coin.symbol.lower())
#                     if user_balance_main_coin.balance == 0:
#                         print('{} на балансе {}'.format(user_pair.pair.main_coin.symbol.upper(),
#                                                         user_balance_main_coin.balance))
#                         continue
#                     if user_balance_main_coin.balance < user_need_to_buy_on_prior_in_first_coin:
#                         user_need_to_buy_on_prior_in_first_coin = user_balance_main_coin.balance
#                 except UserBalance.DoesNotExist:
#                     print('Не нашел такой валюты у пользователя')
#                     continue
#                 price = calculate_price(user_need_to_buy_on_prior_in_first_coin, o_type='buy', bids=bids)
#                 amount = user_need_to_buy_on_prior_in_first_coin / price
#                 print('Хочу потратить {} {} чтобы купить {} {}'.format(user_need_to_buy_on_prior_in_first_coin,
#                                                                        user_pair.pair.main_coin.symbol.upper(),
#                                                                        amount,
#                                                                        user_pair.pair.second_coin.symbol.upper()))
#                 print('Считал по {}'.format(price))
#                 ue_apisecret = user_pair.user_exchange.apisecret.encode()
#                 session = Poloniex(apikey=user_pair.user_exchange.apikey, secret=ue_apisecret)
#                 try:
#                     order = session.buy(
#                         currencyPair=user_pair.pair.main_coin.symbol.upper() + '_' + user_pair.pair.second_coin.symbol.upper(),
#                         rate=price,
#                         amount=amount,
#                         postOnly=1
#                     )
#                     print(order)
#                     pull_user_balances.delay(user_pair.user_exchange.pk)
#                     user_order = UserOrder()
#                     user_order.ue = user_pair.user_exchange
#                     user_order.pair = user_pair.pair
#                     user_order.order_type = 'buy'
#                     user_order.order_number = order['orderNumber']
#                     user_order.first_coin_before = user_balance_main_coin.balance
#                     user_order.second_coin_before = user_balance_second_coin.balance
#                     user_order.price = price
#                     user_order.amount = amount
#                     user_order.total = user_need_to_buy_on_prior_in_first_coin
#                     user_order.fee = _D('0.0015')
#                     user_order.save()
#                 except PoloniexCommandException:
#                     pass
#     return True
#
#
# @shared_task
# def start_calculate_poloniex_sell(args):
#     data = json.loads(args)
#     pair = Pair.objects.get(pk=data['pair'])
#     asks = data['asks']
#     change_rate = _D(data['change_rate'])
#     print('Пара {}'.format(pair.main_coin.symbol.upper() + '_' + pair.second_coin.symbol.upper()))
#     print("Коэфициент цены: {}".format(change_rate))
#
#     user_pairs = UserPair.objects.filter(pair=pair, rate_of_change__lte=abs(change_rate),
#                                          user_exchange__is_active_script=True,
#                                          user_exchange__exchange__exchange='poloniex', rate_of_change__gt=0)
#     print(user_pairs)
#     for user_pair in user_pairs:
#         user_have_second_coin = UserBalance.objects.get(ue=user_pair.user_exchange,
#                                                         coin=user_pair.pair.second_coin.symbol.lower())
#         price = calculate_price(amount=user_have_second_coin.balance, o_type='sell', asks=asks)
#         print('Нашел цену: ' + str(price))
#         print('Хочу потратить {} {} чтобы купить {} {}'.format(user_have_second_coin.balance,
#                                                                user_pair.pair.second_coin.symbol.upper(),
#                                                                user_have_second_coin.balance * _D(price),
#                                                                user_pair.pair.main_coin.symbol.upper()))
#         print('asks')
#         for i in asks:
#             print(i)


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
