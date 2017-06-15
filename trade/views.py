import requests
import re
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from trade.forms import UserExchangesForm, UserWalletForm
from trade.models import UserExchanges, Exchanges, UserBalance, UserWallet, Wallets


@login_required
def index(request):
    args = {'exchange_form': UserExchangesForm(),
            'wallet_form': UserWalletForm(),
            'ue': UserExchanges.objects.filter(user=request.user),
            'uw': UserWallet.objects.filter(user=request.user)}
    if request.method == 'POST':
        re_type = request.POST.get('type')
        if re_type == 'exchange':
            ue = UserExchanges()
            ue.user = request.user
            ue.exchange = Exchanges.objects.get(pk=request.POST.get('exchange'))
            ue.apikey = request.POST.get('apikey')
            ue.apisecret = request.POST.get('apisecret')
            ue.total_btc = float(0)
            ue.save()
            get_exchange_coins(ue=ue)
        elif re_type == 'wallet':
            uw = UserWallet()
            uw.user = request.user
            uw.address = request.POST.get('address')
            uw.wallet = Wallets.objects.get(pk=request.POST.get('wallet'))
            uw.save()
        return render(request, 'trade/index.html', args)
    else:
        return render(request, 'trade/index.html', args)


def change_status(request):
    try:
        ue = UserExchanges.objects.get(pk=request.POST['ue'])
    except ObjectDoesNotExist:
        return HttpResponse('none', status=200)
    ue.is_active = not ue.is_active
    ue.save()
    return HttpResponse('ok', status=200)


def get_exchange_coins(ue=None):
    if ue.exchange.exchange == 'bittrex':
        coins = requests.get('https://bittrex.com/api/v1.1/public/getcurrencies').json()
        for coin in coins['result']:
            new_user_coin = UserBalance()
            new_user_coin.ue = ue
            new_user_coin.coin = coin['Currency'].lower()
            new_user_coin.save()
    elif ue.exchange.exchange == 'poloniex':
        coins = requests.get('https://poloniex.com/public?command=returnCurrencies').json()
        for coin in coins:
            new_user_coin = UserBalance()
            new_user_coin.ue = ue
            new_user_coin.coin = coin.lower()
            new_user_coin.save()
    elif ue.exchange.exchange == 'btc-e':
        coins = requests.get('https://btc-e.nz/api/3/info').json()
        pairs = list(coins['pairs'].keys())
        for item in pairs:
            m = re.match(r'([a-zA-Z0-9]+)_([a-zA-Z0-9]+)', item)
            if m:
                coin_one_name = m.group(1)
                try:
                    user_coin = UserBalance.objects.get(ue=ue, coin=coin_one_name.lower())
                except UserBalance.DoesNotExist:
                    user_coin = None
                if user_coin is None:
                    new_user_coin = UserBalance()
                    new_user_coin.ue = ue
                    new_user_coin.coin = coin_one_name.lower()
                    new_user_coin.save()
                coin_two_name = m.group(2)
                try:
                    user_coin = UserBalance.objects.get(ue=ue, coin=coin_two_name.lower())
                except UserBalance.DoesNotExist:
                    user_coin = None
                if user_coin is None:
                    new_user_coin = UserBalance()
                    new_user_coin.ue = ue
                    new_user_coin.coin = coin_two_name.lower()
                    new_user_coin.save()
