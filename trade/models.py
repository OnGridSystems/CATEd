import datetime
from django.contrib.auth.models import User
from django.db import models
from pytz import utc


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
    apikey = models.CharField(max_length=255)
    apisecret = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    is_correct = models.BooleanField(default=True)
    total_btc = models.DecimalField(max_digits=30, decimal_places=8)
    error = models.CharField(max_length=1000, blank=True)

    def __str__(self):
        return self.user.username + ': ' + self.exchange.exchange

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
    balance = models.DecimalField(max_digits=30, decimal_places=8, default=0)

    def __str__(self):
        return '<' + self.user.username + ' ' + self.wallet.name + ': ' + str(self.balance) + '>'

    class Meta:
        verbose_name = 'Кошелёк пользователя'
        verbose_name_plural = 'Кошельки пользователей'


class WalletHistory(models.Model):
    uw = models.ForeignKey(UserWallet)
    number = models.IntegerField(blank=False, null=False)
    date = models.DateTimeField(blank=False)
    t_from = models.TextField()
    t_to = models.TextField()
    type = models.CharField(max_length=255)
    value = models.BigIntegerField()
    block_hash = models.CharField(max_length=511)
    hash = models.CharField(max_length=511)

    def __str__(self):
        return '<' + self.uw.user.username + ' ' + self.type + ' ' + str(self.value) + '>'

    class Meta:
        verbose_name = 'История кошелька'
        verbose_name_plural = 'Истории кошельков'
