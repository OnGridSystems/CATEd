from django import template

register = template.Library()


@register.filter(name='value_to_eth')
def value_to_eth(value):
    return str(round(float(value / (10 ** 18)), 8)) + ' ETH'
