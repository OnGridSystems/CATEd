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


class UserPair(models.Model):
    user = models.ForeignKey(User)
    user_exchange = models.ForeignKey(UserExchanges)
    pair = models.ForeignKey('Pair')
    rank = models.PositiveIntegerField(default=1)
    rate_of_change = models.DecimalField(max_digits=20, decimal_places=8, default=0)

    class Meta:
        verbose_name = "Пара пользователя"
        verbose_name_plural = "Пары пользователей"


class UserCoinShare(models.Model):
    user_exchange = models.ForeignKey(UserExchanges)
    coin = models.ForeignKey(ExchangeCoin)
    share = models.DecimalField(decimal_places=2, max_digits=5, default=0)

    def __str__(self):
        return self.user_exchange.exchange.exchange + ': ' + self.coin.symbol + ' ' + str(self.share)

    class Meta:
        verbose_name = 'Доля валюты'
        verbose_name_plural = 'Доли валют'


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
        return self.main_coin.exchange.exchange + ': ' + self.main_coin.symbol.upper() + '_' + \
               self.second_coin.symbol.upper()

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


class ExchangeTicker(models.Model):
    exchange = models.ForeignKey(Exchanges)
    pair = models.ForeignKey(Pair)
    high = models.DecimalField(max_digits=30, decimal_places=15)
    last = models.DecimalField(max_digits=30, decimal_places=15)
    low = models.DecimalField(max_digits=30, decimal_places=15)
    bid = models.DecimalField(max_digits=30, decimal_places=15)
    ask = models.DecimalField(max_digits=30, decimal_places=15)
    base_volume = models.DecimalField(max_digits=30, decimal_places=15)
    percent_change = models.DecimalField(max_digits=10, decimal_places=8, default=0)
    date_time = models.DateTimeField(auto_now=True, blank=False, null=False)

    def __str__(self):
        return self.exchange.exchange + ': ' + self.pair.main_coin.name.upper() + '-' + self.pair.second_coin.name.upper()


class Order(models.Model):
    ue = models.ForeignKey(UserExchanges)
    pair = models.CharField(max_length=50)
    globalTradeID = models.BigIntegerField()
    tradeID = models.BigIntegerField()
    orderNumber = models.BigIntegerField()
    category = models.CharField(max_length=50)
    type = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    rate = models.DecimalField(max_digits=20, decimal_places=8)
    fee = models.DecimalField(max_digits=10, decimal_places=8)
    total = models.DecimalField(max_digits=20, decimal_places=8)
    our_total = models.DecimalField(max_digits=20, decimal_places=8)
    is_ok = models.CharField(max_length=5)
    date_time = models.DateTimeField()


class ToTrade(models.Model):
    user_pair = models.ForeignKey(UserPair, blank=False, null=False)
    percent_react = models.DecimalField(max_digits=16, decimal_places=8, blank=False, null=False)
    type = models.CharField(max_length=10, blank=False, null=False)
    price = models.DecimalField(max_digits=16, decimal_places=8, blank=False, null=False)
    amount = models.DecimalField(max_digits=16, decimal_places=8, blank=False, null=False)
    total = models.DecimalField(max_digits=16, decimal_places=8, blank=False, null=False)
    total_f = models.DecimalField(max_digits=16, decimal_places=8, blank=False, null=False, default=0)
    fee = models.DecimalField(max_digits=16, decimal_places=8, blank=False, null=False)
    cause = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user_pair.pair) + ' ' + self.type

    class Meta:
        verbose_name = 'Пара готовая к торговле'
        verbose_name_plural = 'Пары готовые к торговле'

