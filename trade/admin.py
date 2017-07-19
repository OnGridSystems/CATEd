from django.contrib import admin
from .models import Exchanges, UserExchanges, UserBalance, Coin, Wallets, UserWallet, UserHoldings, Transaction


class TransactionAdmin(admin.ModelAdmin):
    list_display = ['name', 't_type', 'date', 'type', 'value']

    class Meta:
        model = Transaction


admin.site.register(Exchanges)
admin.site.register(UserExchanges)
admin.site.register(UserBalance)
admin.site.register(Coin)
admin.site.register(Wallets)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(UserWallet)
admin.site.register(UserHoldings)
