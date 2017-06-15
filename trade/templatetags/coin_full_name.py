from django import template
from django.template.defaultfilters import stringfilter
from trade.models import Coin

register = template.Library()


@register.filter(name='get_full_name')
@stringfilter
def get_full_name(short_name):
    try:
        coin = Coin.objects.get(short_name=short_name.upper())
        return str(coin.full_name)
    except Coin.DoesNotExist:
        return '-'
