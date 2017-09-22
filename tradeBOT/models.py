from django.contrib.auth.models import User
from django.db import models
from trade.models import Exchanges, UserExchange


# Create your models here.
class ExchangeCoin(models.Model):
    exchange = models.ForeignKey(Exchanges)
    symbol = models.CharField(max_length=10)
    rank = models.IntegerField(default=0)

    def __str__(self):
        return self.exchange.name + ' ' + self.symbol

    class Meta:
        verbose_name = "Монета биржи"
        verbose_name_plural = "Монеты биржи"


class UserPair(models.Model):
    user = models.ForeignKey(User)
    user_exchange = models.ForeignKey(UserExchange)
    pair = models.ForeignKey('Pair')
    rank = models.PositiveIntegerField(default=1)
    rate_of_change = models.DecimalField(max_digits=20, decimal_places=8, default=0)

    class Meta:
        verbose_name = "Пара пользователя"
        verbose_name_plural = "Пары пользователей"

    def __str__(self):
        return str(self.user_exchange) + ': ' + self.pair.main_coin.symbol.upper() + '_' + self.pair.second_coin.symbol.upper()

class UserCoinShare(models.Model):
    user_exchange = models.ForeignKey(UserExchange)
    coin = models.ForeignKey(ExchangeCoin)
    share = models.DecimalField(decimal_places=2, max_digits=5, default=0)

    def __str__(self):
        return self.user_exchange.exchange.name + ': ' + self.coin.symbol + ' ' + str(self.share)

    class Meta:
        verbose_name = 'Доля валюты'
        verbose_name_plural = 'Доли валют'


class ExchangeMainCoin(models.Model):
    coin = models.ForeignKey(ExchangeCoin)

    def __str__(self):
        return self.coin.exchange.name + ': ' + self.coin.symbol

    class Meta:
        verbose_name = "Главная монета биржи"
        verbose_name_plural = "Главные монеты биржи"


class Pair(models.Model):
    main_coin = models.ForeignKey(ExchangeCoin, related_name='%(class)s_main_coin')
    second_coin = models.ForeignKey(ExchangeCoin, related_name='%(class)s_second_coin')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.main_coin.exchange.name + ': ' + self.main_coin.symbol.upper() + '_' + \
               self.second_coin.symbol.upper()

    class Meta:
        verbose_name = "Пара"
        verbose_name_plural = "Пары"


class UserMainCoinPriority(models.Model):
    user_exchange = models.ForeignKey(UserExchange)
    main_coin = models.ForeignKey(ExchangeMainCoin)
    priority = models.PositiveIntegerField()
    is_active = models.BooleanField()

    def __str__(self):
        return '%s %s' % (self.user_exchange.exchange.name, self.main_coin)

    class Meta:
        verbose_name_plural = 'Главные монеты пользователей'
        verbose_name = 'Главная монета пользователя'


class CoinMarketCupCoin(models.Model):
    coin_market_id = models.CharField(max_length=63, verbose_name="Внутренее имя", default='')
    name = models.CharField(max_length=63, verbose_name="Имя")
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
    base_volume = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)
    percent_change = models.DecimalField(max_digits=10, decimal_places=8, default=0)
    date_time = models.DateTimeField(blank=False, null=False)

    def __str__(self):
        return self.exchange.name + ': ' + self.pair.main_coin.symbol.upper() + '-' + self.pair.second_coin.symbol.upper()


class Order(models.Model):
    ue = models.ForeignKey(UserExchange)
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


class UserOrder(models.Model):
    ue = models.ForeignKey(UserExchange)
    pair = models.ForeignKey(Pair)
    order_type = models.CharField(max_length=5)
    order_number = models.BigIntegerField()
    main_coin_before_total = models.DecimalField(max_digits=20, decimal_places=10)
    main_coin_before_free = models.DecimalField(max_digits=20, decimal_places=10)
    main_coin_before_used = models.DecimalField(max_digits=20, decimal_places=10)
    second_coin_before_total = models.DecimalField(max_digits=20, decimal_places=10)
    second_coin_before_free = models.DecimalField(max_digits=20, decimal_places=10)
    second_coin_before_used = models.DecimalField(max_digits=20, decimal_places=10)
    main_coin_after_total = models.DecimalField(max_digits=20, decimal_places=10, default=None, blank=True, null=True)
    main_coin_after_free = models.DecimalField(max_digits=20, decimal_places=10, default=None, blank=True, null=True)
    main_coin_after_used = models.DecimalField(max_digits=20, decimal_places=10, default=None, blank=True, null=True)
    second_coin_after_total = models.DecimalField(max_digits=20, decimal_places=10, default=None, blank=True, null=True)
    second_coin_after_free = models.DecimalField(max_digits=20, decimal_places=10, default=None, blank=True, null=True)
    second_coin_after_used = models.DecimalField(max_digits=20, decimal_places=10, default=None, blank=True, null=True)
    price = models.DecimalField(max_digits=20, decimal_places=10)
    amount = models.DecimalField(max_digits=20, decimal_places=10)
    total = models.DecimalField(max_digits=20, decimal_places=10)
    fee = models.DecimalField(max_digits=8, decimal_places=5)
    fact_total = models.DecimalField(max_digits=20, decimal_places=10, default=None, blank=True, null=True)
    fact_fee = models.DecimalField(max_digits=7, decimal_places=5, default=None, blank=True, null=True)
    is_ok = models.NullBooleanField(default=None, blank=True, null=True)
    interim_main_coin = models.DecimalField(max_digits=20, decimal_places=10)
    date_created = models.DateTimeField(auto_now_add=True)
    date_cancel = models.DateTimeField(default=None, blank=True, null=True)
    cancel_desc = models.CharField(max_length=100, blank=True, null=True, default=None)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ue.user.username + ' ' + self.ue.exchange.name + ': ' + self.order_type + ' ' + self.pair.main_coin.symbol.upper() + '_' + self.pair.second_coin.symbol.upper()

    class Meta:
        verbose_name_plural = 'Ордера пользователей'
        verbose_name = 'Ордер пользователя'


class ToTrade(models.Model):
    user_pair = models.ForeignKey(UserPair, blank=False, null=False)
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


class Сalculations(models.Model):
    user_pair = models.ForeignKey(UserPair)
    type = models.CharField(max_length=10)
    depth_coef = models.DecimalField(max_digits=16, decimal_places=8, blank=False, null=False)
    price = models.DecimalField(max_digits=16, decimal_places=8, blank=False, null=False)
    amount = models.DecimalField(max_digits=16, decimal_places=8, blank=False, null=False)
    bids = models.TextField(blank=True, null=True)
    asks = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now=True)
