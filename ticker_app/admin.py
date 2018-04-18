from django.contrib import admin
from ticker_app import models


class ExchangeTickerAdmin(admin.ModelAdmin):
    list_display = [field.name for field in models.ExchangeTicker._meta.fields]

    class Meta:
        model = models.ExchangeTicker

admin.site.register(models.ExchangeTicker, ExchangeTickerAdmin)
