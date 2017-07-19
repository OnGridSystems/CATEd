from django import template
from tradeBOT.models import ExchangeMainCoin, Pair

register = template.Library()


@register.inclusion_tag('tradeBOT/exchange_primary_coins.html')
def exchange_primary_coins(exchange):
    try:
        primary_coins = ExchangeMainCoin.objects.filter(coin__exchange=exchange)
        return {'primary_coins': primary_coins}
    except ExchangeMainCoin.DoesNotExist:
        return None


@register.inclusion_tag('tradeBOT/primary_coin_pairs.html')
def primary_coin_pairs(primary_coin):
    try:
        pairs = Pair.objects.filter(main_coin=primary_coin.coin)
        return {'pairs': pairs}
    except Pair.DoesNotExist:
        return None
