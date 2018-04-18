from django.db import models
from trade import models as trade_models


# Create your models here.
class ExchangeTicker(models.Model):
    exchange_id = models.IntegerField()
    pair_id = models.IntegerField()
    high = models.DecimalField(max_digits=30, decimal_places=15)
    last = models.DecimalField(max_digits=30, decimal_places=15)
    low = models.DecimalField(max_digits=30, decimal_places=15)
    bid = models.DecimalField(max_digits=30, decimal_places=15)
    ask = models.DecimalField(max_digits=30, decimal_places=15)
    base_volume = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)
    percent_change = models.DecimalField(max_digits=10, decimal_places=8, default=0)
    date_time = models.DateTimeField(blank=False, null=False)

    def __str__(self):
        # return trade_models.Exchanges.objects.get(pk=self.exchange_id).name + ': ' + self.pair.main_coin.symbol.upper() + '-' + self.pair.second_coin.symbol.upper()
        return '{}: {}'.format(self.exchange_id, self.pair_id)

    class Meta:
        verbose_name = 'Данные тикера'
        verbose_name_plural = 'Данные тикеров'
