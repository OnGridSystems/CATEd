from django import template

from trade.models import Exchanges
from tradeBOT.models import ExchangeCoin

register = template.Library()


@register.inclusion_tag('tradeBOT/Coins.html')
def exchange_coins(exch):
    exchange = Exchanges.objects.get(exchange=exch)
    exch_coins = ExchangeCoin.objects.filter(exchange=exchange).order_by('-is_active', 'name')
    return {
        'exch': exchange,
        'coins': exch_coins,
    }
