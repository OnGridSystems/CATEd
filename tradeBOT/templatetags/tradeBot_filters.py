from django import template
from tradeBOT.models import UserDeactivatedPairs, CoinMarketCupCoin, UserMainCoinPriority
from trade.models import UserBalance

register = template.Library()


@register.filter(name='is_active_pair')
def is_active_pair(pair, user_exchange):
    umcp = is_deactivate = None
    unactive = False
    try:
        is_deactivate = UserDeactivatedPairs.objects.get(pair=pair, user_exchange=user_exchange)
    except UserDeactivatedPairs.DoesNotExist:
        pass
    try:
        umcp = UserMainCoinPriority.objects.get(user_exchange=user_exchange, main_coin__coin=pair.main_coin)
    except UserMainCoinPriority.DoesNotExist:
        pass
    if umcp is not None:
        if umcp.is_active is False:
            unactive = True
    if is_deactivate is not None:
        unactive = True
    if unactive:
        return 'unactive'


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
