from django.contrib.auth.models import User
from django.db import models
from trade.models import Exchanges, UserExchanges


# Create your models here.
class ExchangeCoin(models.Model):
    exchange = models.ForeignKey(Exchanges)
    name = models.CharField(max_length=25)
    symbol = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.exchange.exchange + ' ' + self.symbol

    class Meta:
        verbose_name = "Монета биржи"
        verbose_name_plural = "Монеты биржи"


class UserCoin(models.Model):
    user = models.ForeignKey(User)
    coin = models.ForeignKey(ExchangeCoin)
    user_exchange = models.ForeignKey(UserExchanges)
    share = models.DecimalField(decimal_places=2, max_digits=5, default=0)
    rank = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.user.username + ' ' + self.coin.symbol

    class Meta:
        verbose_name = "Монета пользователя"
        verbose_name_plural = "Монеты пользователя"


class ExchangeMainCoin(models.Model):
    coin = models.ForeignKey(ExchangeCoin)
    total = models.DecimalField(max_digits=25, decimal_places=8)

    def __str__(self):
        return self.coin.exchange.exchange + ': ' + self.coin.name + ' ' + str(self.total)

    class Meta:
        verbose_name = "Главная монета биржи"
        verbose_name_plural = "Главные монеты биржи"


class Pair(models.Model):
    main_coin = models.ForeignKey(ExchangeCoin, related_name='%(class)s_main_coin')
    second_coin = models.ForeignKey(ExchangeCoin, related_name='%(class)s_second_coin')

    def __str__(self):
        return self.main_coin.exchange.exchange + ': ' + self.main_coin.name + ' - ' + self.second_coin.name

    class Meta:
        verbose_name = "Пара"
        verbose_name_plural = "Пары"


class UserMainCoinPriority(models.Model):
    user_exchange = models.ForeignKey(UserExchanges)
    main_coin = models.ForeignKey(ExchangeMainCoin)
    priority = models.PositiveIntegerField()
    is_active = models.BooleanField()

    def __str__(self):
        return '%s %s' % (self.user_exchange.exchange.exchange, self.main_coin)

    class Meta:
        verbose_name_plural = 'Главные монеты пользователей'
        verbose_name = 'Главная монета пользователя'


class UserDeactivatedPairs(models.Model):
    pair = models.ForeignKey(Pair)
    user_exchange = models.ForeignKey(UserExchanges)


class CoinMarketCupCoin(models.Model):
    coin_market_id = models.CharField(max_length=63, verbose_name="Внутренее имя", default='')
    name = models.CharField(max_length=63, verbose_name="Имя", unique=True)
    symbol = models.CharField(max_length=15, verbose_name="Аббр")
    rank = models.PositiveIntegerField()
    price_usd = models.DecimalField(decimal_places=8, max_digits=30, verbose_name="Цена в USD")
    volume_usd_24h = models.DecimalField(decimal_places=8, max_digits=30, null=True)
    available_supply = models.DecimalField(decimal_places=8, max_digits=30, null=True)
    total_supply = models.DecimalField(decimal_places=8, max_digits=30, null=True)

    class Meta:
        verbose_name = 'Монета CoinMarketCup'
        verbose_name_plural = 'Монеты CoinMarketCup'

    def __str__(self):
        return self.name + ' ' + self.symbol
