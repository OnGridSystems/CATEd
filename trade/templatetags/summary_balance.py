from django import template
from trade.models import UserWallet, UserExchange
import requests

register = template.Library()


@register.filter
def get_user_summaries_btc(user):
    btc_total = float(0)
    usd_total = float(0)
    wallets = UserWallet.objects.all()
    exchanges = UserExchange.objects.all()
    if wallets is not None:
        for wallet in wallets:
            usd_total += float(wallet.total_usd)
    if exchanges is not None:
        for exchange in exchanges:
            usd_total += float(exchange.total_usd)
    if usd_total > 0:
        btc_price = requests.get('https://api.cryptonator.com/api/full/btc-usd').json()
        btc_total = usd_total / float(btc_price['ticker']['price'])
    return btc_total


@register.filter
def get_user_summaries_usd(user):
    usd_total = float(0)
    wallets = UserWallet.objects.all()
    exchanges = UserExchange.objects.all()
    if wallets is not None:
        for wallet in wallets:
            usd_total += float(wallet.total_usd)
    if exchanges is not None:
        for exchange in exchanges:
            usd_total += float(exchange.total_usd)
    return usd_total


@register.filter
def as_percent_of(part, whole):
    try:
        return float(part) / whole * 100
    except (ValueError, ZeroDivisionError):
        return 0
