from django import template
from tradeBOT.models import CoinMarketCupCoin

register = template.Library()


@register.inclusion_tag('tradeBOT/coin_info.html')
def coin_info(symbol):
    try:
        coin = CoinMarketCupCoin.objects.get(symbol=symbol)
    except CoinMarketCupCoin.DoesNotExist:
        return None
    except CoinMarketCupCoin.MultipleObjectsReturned:
        return None
    return {'coin': coin}
