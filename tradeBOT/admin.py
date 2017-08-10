from django.contrib import admin
from django.db.models.functions import Lower

from tradeBOT import models


class UserPairInline(admin.TabularInline):
    model = models.UserPair


class ExchangeCoinAdmin(admin.ModelAdmin):
    search_fields = ['symbol', 'name']
    list_filter = ['exchange']

    class Meta:
        model = models.ExchangeCoin


class UserPairAdmin(admin.ModelAdmin):
    list_display = [field.name for field in models.UserPair._meta.fields]
    list_filter = ['user', 'pair__main_coin__exchange__exchange']

    class Meta:
        model = models.UserPair


class CoinMarketCupCoinAdmin(admin.ModelAdmin):
    search_fields = ['name', 'symbol']

    def get_ordering(self, request):
        return ['rank']

    class Meta:
        model = models.CoinMarketCupCoin


class PairAdmin(admin.ModelAdmin):
    search_fields = ['main_coin', 'second_coin']
    list_filter = ['main_coin__exchange__exchange']
    inlines = [UserPairInline]


class ExchangeTickerAdmin(admin.ModelAdmin):
    list_display = [field.name for field in models.ExchangeTicker._meta.fields]
    list_filter = ['exchange', 'pair']

    class Meta:
        model = models.ExchangeTicker


class OrderAdmin(admin.ModelAdmin):
    list_display = [field.name for field in models.Order._meta.fields]
    list_filter = ['pair', 'ue']
    search_fields = ['orderNumber']

    class Meta:
        model = models.Order


class ToTradeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in models.ToTrade._meta.fields]
    list_filter = ['user_pair__user_exchange', 'type', 'user_pair__pair']

    class Meta:
        model = models.ToTrade


admin.site.register(models.ExchangeCoin, ExchangeCoinAdmin)
admin.site.register(models.UserPair, UserPairAdmin)
admin.site.register(models.Pair, PairAdmin)
admin.site.register(models.ExchangeMainCoin)
admin.site.register(models.CoinMarketCupCoin, CoinMarketCupCoinAdmin)
admin.site.register(models.UserMainCoinPriority)
admin.site.register(models.ExchangeTicker, ExchangeTickerAdmin)
admin.site.register(models.Order, OrderAdmin)
admin.site.register(models.ToTrade, ToTradeAdmin)
