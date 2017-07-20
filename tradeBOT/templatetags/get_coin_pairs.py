from tradeBOT.models import Pair, UserCoin
from django import template
from django.db.models import Q

register = template.Library()


@register.inclusion_tag('tradeBOT/pairs.html')
def coin_pairs(coin, user, user_exchange):
    user_coins = UserCoin.objects.filter(user_exchange=user_exchange)
    coins = []
    for uc in user_coins:
        coins.append(uc.coin)
    try:
        pairs = Pair.objects.filter(
            (Q(main_coin=coin.coin) & Q(second_coin__in=coins)) | (Q(second_coin=coin.coin) & Q(main_coin__in=coins)))
    except Pair.DoesNotExist:
        pairs = None
    return {'pairs': pairs,
            'user': user,
            'user_exchange': user_exchange}
