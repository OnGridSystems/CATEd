from django import template

from ticker_app.models import ExchangeTicker
from tradeBOT.models import CoinMarketCupCoin, UserMainCoinPriority, Pair, ExchangeMainCoin, UserPair
from trade.models import UserBalance

register = template.Library()


@register.filter(name='user_have_coin')
def user_holdings(coin_symbol, user_exchange):
    try:
        user_hold = UserBalance.objects.get(ue_id=user_exchange, coin=coin_symbol)
        return user_hold.total
    except UserBalance.DoesNotExist:
        return 0


@register.filter(name='get_coinmarket_id')
def get_coinmarket_id(symbol):
    try:
        coin_market_id = CoinMarketCupCoin.objects.filter(symbol=symbol).earliest('rank')
        return coin_market_id.coin_market_id
    except CoinMarketCupCoin.DoesNotExist:
        return ''


@register.inclusion_tag('tradeBOT/user_primary.html')
def get_user_primary_coins(user_exchange, primary_coin):
    try:
        umcp = UserMainCoinPriority.objects.get(user_exchange=user_exchange, main_coin=primary_coin)
        return {'coin': umcp,
                'success': True}
    except UserMainCoinPriority.DoesNotExist:
        return {'success': False}


@register.inclusion_tag('tradeBOT/get_primary_pairs.html')
def get_primary_pairs(coin, user_exchange):
    try:
        pairs = Pair.objects.filter(main_coin=coin, second_coin__rank__lte=100).order_by('is_active',
                                                                                         'second_coin__symbol')
        return {'pairs': pairs, 'user_exchange': user_exchange}
    except Pair.DoesNotExist:
        return None


@register.filter(name='get_last')
def get_last(pair, user_exchange):
    # return 0
    max_pk = ExchangeTicker.objects.filter(exchange_id=user_exchange.exchange.pk, pair_id=pair.pk).order_by(
        '-id').first().pk
    ticker = ExchangeTicker.objects.get(pk=max_pk).last
    if ticker is not None:
        return round(ticker, 8)
    else:
        return 0


@register.filter(name='get_change_percent')
def get_change_percent(pair, user_exchange):
    # return 0
    max_pk = ExchangeTicker.objects.filter(exchange_id=user_exchange.exchange.pk, pair_id=pair.pk).order_by(
        '-id').first().pk
    ticker = ExchangeTicker.objects.get(pk=max_pk).percent_change
    if ticker is not None:
        return round(ticker * 100, 2)
    else:
        return 0


@register.filter(name='is_pair_active')
def is_pair_active(user_pair, user_exchange_pk):
    main_coin = user_pair.pair.main_coin
    try:
        exch_primary = ExchangeMainCoin.objects.get(coin=main_coin)
        user_primary_coin = UserMainCoinPriority.objects.get(user_exchange_id=user_exchange_pk, main_coin=exch_primary)
        return user_primary_coin.is_active
    except ExchangeMainCoin.DoesNotExist:
        return False
    except UserMainCoinPriority.DoesNotExist:
        return True


@register.filter(name='user_pair_rate_of_change')
def user_pair_rate_of_change(user_pair_pk):
    try:
        user_pair = UserPair.objects.get(pk=user_pair_pk)
        return user_pair.rate_of_change
    except UserPair.DoesNotExist:
        return float(0)


@register.filter(name='user_pair_interval_change')
def user_pair_interval_change(user_pair_pk):
    try:
        user_pair = UserPair.objects.get(pk=user_pair_pk)
        return user_pair.change_interval
    except UserPair.DoesNotExist:
        return 0


@register.filter(name='multiple')
def multiple(value, factor):
    return value * factor


@register.filter(name='haven_percent')
def haven_percent(coin, ue):
    try:
        user_balance = UserBalance.objects.get(ue=ue, coin=coin.symbol.lower())
        coin_total_btc = user_balance.btc_value
    except UserBalance.DoesNotExist:
        coin_total_btc = 0
    return coin_total_btc / (ue.total_btc / 100)
