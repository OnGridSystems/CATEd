import json

import requests
import re
import djangoTrade.settings as settings
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from trade.forms import UserExchangesForm, UserWalletForm
from trade.models import UserExchanges, Exchanges, UserBalance, UserWallet, Wallets, Transaction, UserHoldings
from yandex_money.api import Wallet, ExternalPayment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@login_required
def index(request):
    transaction = Transaction.objects.all()
    paginator = Paginator(transaction, 100)
    page = request.GET.get('page')
    try:
        transactions = paginator.page(page)
    except PageNotAnInteger:
        transactions = paginator.page(1)
    except EmptyPage:
        transactions = paginator.page(paginator.num_pages)
    args = {'exchange_form': UserExchangesForm(),
            'wallet_form': UserWalletForm(),
            'ue': UserExchanges.objects.all(),
            'uw': UserWallet.objects.all(),
            'trans': transactions}
    return render(request, 'trade/home.html', args)


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


@login_required
def exchange(request):
    if request.method == 'POST':
        ue = UserExchanges()
        ue.user = request.user
        ue.exchange = Exchanges.objects.get(pk=request.POST.get('exchange'))
        ue.apikey = request.POST.get('apikey')
        ue.apisecret = request.POST.get('apisecret')
        ue.total_btc = float(0)
        ue.save()
        get_exchange_coins(ue=ue)
    return redirect(index)


@login_required
def wallet(request):
    if request.method == 'POST':
        wallet = Wallets.objects.get(pk=request.POST.get('wallet'))
        if wallet.name == 'Yandex Money':
            scope = ['account-info', 'operation-history', 'operation-details']
            auth_url = Wallet.build_obtain_token_url(
                client_id=settings.YANDEX_MONEY_CLIENT_ID,
                redirect_uri=settings.YANDEX_MONEY_REDIRECT_URI,
                scope=scope) + '&response_type=code'
            return redirect(auth_url)
        else:
            uw = UserWallet()
            uw.user = request.user
            uw.address = request.POST.get('address')
            uw.wallet = wallet
            uw.save()
    elif request.method == 'GET':
        access_token = Wallet.get_access_token(
            client_id=settings.YANDEX_MONEY_CLIENT_ID,
            redirect_uri=settings.YANDEX_MONEY_REDIRECT_URI,
            code=request.GET.get('code'),
            client_secret=settings.YANDEX_MONEY_CLIENT_SECRET
        )
        access_token = access_token['access_token']
        wallet = Wallet(access_token)
        account_info = wallet.account_info()
        uw = UserWallet()
        uw.wallet = Wallets.objects.get(name='Yandex Money')
        uw.access_token = access_token
        uw.user = request.user
        uw.address = account_info['account']
        uw.balance = account_info['balance']
        uw.save()
    return redirect(index)


@login_required
def get_holding(request):
    type_r = request.GET.get('type')
    if request.is_ajax():
        if type_r == 'names':
            names = []
            user_hold_names = UserHoldings.objects.values('type').distinct()
            if len(user_hold_names) > 0:
                for name in user_hold_names:
                    names.append(name['type'])
                return HttpResponse(json.dumps(names), status=200)
            else:
                return HttpResponse('none', status=200)
        else:
            holdings = UserHoldings.objects.filter(type=type_r).order_by('date_time')
            list_hold = [obj.as_list() for obj in holdings]
            return HttpResponse(json.dumps(list_hold), status=200)


def add_new_transaction_comment(request):
    if request.POST:
        tr_id = request.POST.get('tr_id')
        comment = request.POST.get('comment')
        try:
            trans = Transaction.objects.get(pk=tr_id)
            trans.user_comment = comment
            trans.save()
        except Transaction.DoesNotExist:
            return HttpResponse('none', status=200)
        return HttpResponse('ok', status=200)
