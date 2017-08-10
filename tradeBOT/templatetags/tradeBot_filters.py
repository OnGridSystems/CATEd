from django import template
from tradeBOT.models import CoinMarketCupCoin, UserMainCoinPriority, Pair, ExchangeTicker, ExchangeMainCoin, UserPair
from trade.models import UserBalance

register = template.Library()


@register.filter(name='user_have_coin')
def user_holdings(coin_symbol, user_exchange):
    try:
        user_hold = UserBalance.objects.get(ue_id=user_exchange, coin=coin_symbol)
        return user_hold.balance
    except UserBalance.DoesNotExist:
        return 0


@register.filter(name='get_coinmarket_id')
def get_coinmarket_id(symbol):
    try:
        coin_market_id = CoinMarketCupCoin.objects.get(symbol=symbol)
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
        pairs = Pair.objects.filter(main_coin=coin)
        return {'pairs': pairs, 'user_exchange': user_exchange}
    except Pair.DoesNotExist:
        return None


@register.filter(name='get_last')
def get_last(pair, user_exchange):
    ticker = ExchangeTicker.objects.filter(exchange=user_exchange.exchange, pair=pair).order_by('-date_time').first()
    if ticker is not None:
        return round(ticker.last, 6)
    else:
        return 0


@register.filter(name='get_change_percent')
def get_change_percent(pair, user_exchange):
    ticker = ExchangeTicker.objects.filter(exchange=user_exchange.exchange, pair=pair).order_by('-date_time').first()
    if ticker is not None:
        return round(ticker.percent_change * 100, 2)
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


@register.filter(name='user_pair_percent_change')
def user_pair_percent_change(user_pair_pk):
    try:
        user_pair = UserPair.objects.get(pk=user_pair_pk)
        return user_pair.change_percent
    except UserPair.DoesNotExist:
        return float(0)


@register.filter(name='user_pair_interval_change')
def user_pair_interval_change(user_pair_pk):
    try:
        user_pair = UserPair.objects.get(pk=user_pair_pk)
        return user_pair.change_interval
    except UserPair.DoesNotExist:
        return 0
