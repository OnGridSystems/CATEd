from django import template
from trade.models import UserBalance

register = template.Library()


@register.inclusion_tag('trade/coins.html')
def get_coins(ue):
    coins = UserBalance.objects.filter(ue=ue).order_by('-balance')
    return {'coins': coins}
