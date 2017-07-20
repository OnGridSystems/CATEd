from django import template
from tradeBOT.models import UserDeactivatedPairs
from trade.models import UserBalance

register = template.Library()


@register.filter(name='is_active_pair')
def is_active_pair(pair, user_exchange):
    try:
        is_deactivate = UserDeactivatedPairs.objects.get(pair=pair, user_exchange=user_exchange)
        return 'unactive'
    except UserDeactivatedPairs.DoesNotExist:
        return ''


@register.filter(name='user_have_coin')
def user_holdings(coin_symbol, user_exchange):
    try:
        user_hold = UserBalance.objects.get(ue_id=user_exchange, coin=coin_symbol)
        return user_hold.balance
    except UserBalance.DoesNotExist:
        return 0
