from django.contrib import admin
from .models import Exchanges, UserExchanges, UserBalance, Coin, Wallets, UserWallet, WalletHistory, UserHoldings

admin.site.register(Exchanges)
admin.site.register(UserExchanges)
admin.site.register(UserBalance)
admin.site.register(Coin)
admin.site.register(Wallets)
admin.site.register(WalletHistory)
admin.site.register(UserWallet)
admin.site.register(UserHoldings)
