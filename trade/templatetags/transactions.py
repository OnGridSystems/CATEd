from django import template
from trade.models import Transaction

register = template.Library()


@register.inclusion_tag('trade/transactions.html')
def get_transactions(uw):
    transactions = Transaction.objects.all().order_by('-date')
    return {'transactions': transactions, 'item': uw}
