from django.contrib import admin
from .models import Exchanges, UserExchange, UserBalance, Coin, Wallets, UserWallet, UserHoldings, Transaction


class TransactionAdmin(admin.ModelAdmin):
    list_display = ['name', 't_type', 'date', 'type', 'value']

    class Meta:
        model = Transaction


class UserBalancesAdmin(admin.ModelAdmin):
    list_display = [field.name for field in UserBalance._meta.fields]
    list_filter = ['ue']

    class Meta:
        model = UserBalance


admin.site.register(Exchanges)
admin.site.register(UserExchange)
admin.site.register(UserBalance, UserBalancesAdmin)
admin.site.register(Coin)
admin.site.register(Wallets)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(UserWallet)
admin.site.register(UserHoldings)
