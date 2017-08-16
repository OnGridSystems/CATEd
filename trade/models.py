import datetime

from decimal import Decimal
from django.contrib.auth.models import User
from django.db import models
from pytz import utc
import time


class Exchanges(models.Model):
    exchange = models.CharField(max_length=255)
    url = models.URLField()
    driver = models.CharField(max_length=255)

    def __str__(self):
        return "<" + self.exchange + ">"

    class Meta:
        verbose_name = "Биржа"
        verbose_name_plural = "Биржи"


class UserExchanges(models.Model):
    user = models.ForeignKey(User)
    exchange = models.ForeignKey(Exchanges)
    apikey = models.CharField(max_length=127)
    apisecret = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    is_active_script = models.BooleanField(default=False)
    is_correct = models.BooleanField(default=True)
    total_btc = models.DecimalField(max_digits=30, decimal_places=8)
    total_usd = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    error = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.user.username + ': ' + self.exchange.exchange + ' (' + str(self.pk) + ')'

    class Meta:
        verbose_name = "Биржа пользователя"
        verbose_name_plural = "Биржи пользователей"


class UserBalance(models.Model):
    ue = models.ForeignKey(UserExchanges)
    coin = models.CharField(max_length=10)
    balance = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    btc_value = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ue.exchange.exchange + ' ' + self.ue.user.username + ' ' + self.coin + ': ' + str(self.balance)

    class Meta:
        verbose_name = "Баланс пользователя"
        verbose_name_plural = "Финансы пользователей"


class Coin(models.Model):
    short_name = models.CharField(max_length=20)
    full_name = models.CharField(max_length=40)

    def __str__(self):
        return '<' + self.short_name + ' ' + self.full_name + '>'

    class Meta:
        verbose_name = 'Криптовалюта'
        verbose_name_plural = 'Криптовалюты'


class Wallets(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Кошелёк'
        verbose_name_plural = "Кошельки"


class UserWallet(models.Model):
    user = models.ForeignKey(User)
    wallet = models.ForeignKey(Wallets)
    address = models.CharField(max_length=511)
    access_token = models.CharField(max_length=511, blank=True, default=None, null=True)
    balance = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    total_btc = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    total_usd = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '<' + self.user.username + ' ' + self.wallet.name + ': ' + str(self.balance) + '>'

    class Meta:
        verbose_name = 'Кошелёк пользователя'
        verbose_name_plural = 'Кошельки пользователей'


class Transaction(models.Model):
    name = models.CharField(max_length=50)
    t_type = models.CharField(max_length=20)
    number = models.BigIntegerField(blank=False, null=False)
    date = models.DateTimeField(blank=False)
    t_from = models.TextField()
    t_to = models.TextField()
    type = models.CharField(max_length=10)
    value = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    block_hash = models.CharField(max_length=127, default=None, null=True)
    hash = models.CharField(max_length=127)
    comment = models.TextField(default='', null=True)
    title = models.CharField(max_length=255, default='', null=True)
    details = models.CharField(max_length=255, default='', null=True)
    usd_value = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    user_comment = models.CharField(max_length=255, blank=True, default=None, null=True)
    currency = models.CharField(max_length=10, blank=True, default=None, null=True)

    def __str__(self):
        return '<' + self.name + ' ' + self.type + ' ' + str(self.value) + '>'

    class Meta:
        verbose_name = 'Транзакциия'
        verbose_name_plural = 'Транзакции'
        unique_together = ('name', 't_type', 'hash')


class UserHoldings(models.Model):
    user = models.ForeignKey(User)
    type = models.CharField(max_length=255)
    total_btc = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    total_usd = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    date_time = models.DateTimeField(blank=False)

    def __str__(self):
        return '<' + self.user.username + ' - ' + self.type + ': ' + str(self.total_btc) + '>'

    class Meta:
        verbose_name_plural = 'Истории балансов'
        verbose_name = 'История баланса'

    def as_list(self):
        return [
            int(time.mktime(self.date_time.timetuple()) * 1000),
            float(Decimal(self.total_btc).quantize(Decimal('.00000001')))
        ]
