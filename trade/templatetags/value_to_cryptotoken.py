from django import template

register = template.Library()


@register.filter(name='value_to_cryptotoken')
def value_to_cryptotoken(value, item):
    if item.wallet.name == 'ETH':
        return str(round(float(value / (10 ** 18)), 8)) + ' ETH'
    elif item.wallet.name == 'BTC':
        return str(round(float(value), 8)) + ' BTC'
    else:
        return '0 RUR'
