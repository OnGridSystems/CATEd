from django import template
from trade.models import WalletHistory

register = template.Library()


@register.inclusion_tag('trade/transactions.html')
def get_transactions(uw):
    transactions = WalletHistory.objects.filter(uw=uw).order_by('-date')
    return {'transactions': transactions, 'item': uw}
