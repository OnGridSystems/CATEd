from django import template
from trade.models import Transaction

register = template.Library()


@register.inclusion_tag('trade/wallet_info.html')
def get_wallet_info(uw):
    transactions = Transaction.objects.filter(name=uw.wallet.name + str(uw.pk)).order_by('-date')
    if len(transactions) > 0:
        in_trans = list(transactions.filter(type='in'))
        out_trans = transactions.filter(type='out')
        in_trans_sum = 0
        out_trans_sum = 0
        for item in in_trans:
            in_trans_sum += item.value
        for item in out_trans:
            out_trans_sum += item.value
        return {'uw': uw,
                'success': 1,
                'total_trans': len(transactions),
                'in_trans': in_trans,
                'out_trans': out_trans,
                'in_trans_sum': in_trans_sum,
                'out_trans_sum': out_trans_sum
                }
    else:
        return {'success': 0}
