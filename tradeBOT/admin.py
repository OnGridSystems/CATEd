from django.contrib import admin
from django.db.models.functions import Lower

from tradeBOT import models


# Register your models here.

class UserCoinInline(admin.TabularInline):
    model = models.UserCoin


class ExchangeCoinAdmin(admin.ModelAdmin):
    search_fields = ['symbol', 'name']
    list_filter = ['exchange']
    inlines = [UserCoinInline, ]

    class Meta:
        model = models.ExchangeCoin


class UserCoinAdmin(admin.ModelAdmin):
    list_filter = ['user']

    class Meta:
        model = models.UserCoin


class CoinMarketCupCoinAdmin(admin.ModelAdmin):
    search_fields = ['name', 'symbol']

    def get_ordering(self, request):
        return ['rank']

    class Meta:
        model = models.CoinMarketCupCoin


class PairAdmin(admin.ModelAdmin):
    search_fields = ['main_coin', 'second_coin']
    list_filter = ['main_coin__exchange__exchange']


class ExchangeTickerAdmin(admin.ModelAdmin):
    list_display = ['exchange', 'pair', 'high', 'last', 'low', 'bid', 'ask', 'percent_change', 'date_time']
    list_filter = ['exchange', 'pair']

admin.site.register(models.ExchangeCoin, ExchangeCoinAdmin)
admin.site.register(models.UserCoin, UserCoinAdmin)
admin.site.register(models.Pair, PairAdmin)
admin.site.register(models.ExchangeMainCoin)
admin.site.register(models.CoinMarketCupCoin, CoinMarketCupCoinAdmin)
admin.site.register(models.UserMainCoinPriority)
admin.site.register(models.ExchangeTicker, ExchangeTickerAdmin)
