from django import template
from trade.models import Transaction, UserWallet

register = template.Library()


@register.filter(name='value_to_cryptotoken')
def value_to_cryptotoken(value, item):
    if type(item) == UserWallet:
        if item.wallet.name == 'ETH':
            return str(round(float(value / (10 ** 18)), 8)) + ' ETH'
        elif item.wallet.name == 'BTC':
            return str(round(float(value), 8)) + ' BTC'
        elif item.wallet.name == 'Yandex Money':
            return str(round(float(value), 2)) + ' RUR'
    elif type(item) == Transaction:
        if item.currency is not None:
            return str(item.value) + ' ' + item.currency
        else:
            if item.name[0] == 'E':
                return str(round(float(value / (10 ** 18)), 8)) + ' ETH'
            elif item.name[0] == 'B':
                return str(round(float(value), 8)) + ' BTC'
            elif item.name[0] == 'Y':
                return str(round(float(value), 2)) + ' RUR'
