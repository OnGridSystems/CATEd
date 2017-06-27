from __future__ import absolute_import, unicode_literals
import os
from celery.schedules import crontab
from celery.task import periodic_task
import datetime
from http.client import HTTPException
from celery import shared_task
import time
import requests
from django.contrib.auth.models import User

from trade.drivers.btce_driver import APIError
from trade.models import UserExchanges, UserBalance, Coin, Exchanges, Wallets, UserWallet, WalletHistory, UserHoldings
from trade.drivers import btce_trader, bittrex_driver
from poloniex import Poloniex, PoloniexCommandException
from yandex_money.api import Wallet, ExternalPayment


@periodic_task(run_every=crontab(minute='*/5'))
def start_trade_btce():
    exchange = Exchanges.objects.get(exchange='btc-e')
    btce_ue = UserExchanges.objects.filter(is_active=True, exchange=exchange)
    if len(btce_ue) > 0:
        for ue in btce_ue:
            totalBtc = float(0)
            try:
                driver = btce_trader.BtceTrader(secret=ue.apisecret, key=ue.apikey)
                try:
                    balances = driver.pull_balances()
                    if balances is not None:
                        for item in balances['funds']:
                            try:
                                user_coin = UserBalance.objects.get(ue=ue, coin=item.lower())
                            except UserBalance.DoesNotExist:
                                user_coin = None
                            if user_coin is None:
                                new_user_coin = UserBalance()
                                new_user_coin.ue = ue
                                new_user_coin.coin = item
                                new_user_coin.balance = balances['funds'][item]
                                btc_value = get_btc_value(coin_name=item, count=balances['funds'][item])
                                new_user_coin.btc_value = btc_value
                                totalBtc += btc_value
                                new_user_coin.save()
                            else:
                                user_coin.balance = balances['funds'][item]
                                btc_value = get_btc_value(coin_name=item, count=balances['funds'][item])
                                user_coin.btc_value = btc_value
                                totalBtc += btc_value
                                user_coin.save()
                except APIError as error:
                    print("Убираю накуй, неверно че-то")
                    ue.error = error
                    ue.is_active = False
                    ue.is_correct = False
                    ue.save()
                ue.total_btc = totalBtc
                ue.total_usd = get_usd_value('btc', totalBtc)
                ue.save()
            except HTTPException:
                print('Ошибка, начинаем заново')

    else:
        print("Никто не включил скрипт")
    return True


@periodic_task(run_every=crontab(minute='*/5'))
def start_trade_poloniex():
    exchange = Exchanges.objects.get(exchange='poloniex')
    poloniex_ue = UserExchanges.objects.filter(is_active=True, exchange=exchange)
    if len(poloniex_ue) > 0:
        for ue in poloniex_ue:
            totalBtc = float(0)
            try:
                ue_apisecret = ue.apisecret.encode()
                driver = Poloniex(secret=ue_apisecret, apikey=ue.apikey)
                try:
                    balances = driver.returnCompleteBalances()
                    if balances is not None:
                        for c in balances.keys():
                            try:
                                user_coin = UserBalance.objects.get(ue=ue, coin=c.lower())
                            except UserBalance.DoesNotExist:
                                user_coin = None
                            if user_coin is None:
                                new_user_coin = UserBalance()
                                new_user_coin.ue = ue
                                new_user_coin.coin = c.lower()
                                new_user_coin.balance = float(balances[c]['available'])
                                new_user_coin.btc_value = float(balances[c]['btcValue'])
                                totalBtc += float(balances[c]['btcValue'])
                                new_user_coin.save()
                            else:
                                user_coin.balance = float(balances[c]['available'])
                                user_coin.btc_value = float(balances[c]['btcValue'])
                                totalBtc += float(balances[c]['btcValue'])
                                user_coin.save()
                except PoloniexCommandException as error:
                    print("Убираю накуй, неверно че-то")
                    ue.error = error
                    ue.is_active = False
                    ue.is_correct = False
                    ue.save()
                ue.total_btc = totalBtc
                ue.total_usd = get_usd_value('btc', totalBtc)
                ue.save()
            except HTTPException:
                print('Ошибка, начинаем заново')

    else:
        print("Никто не включил скрипт")
    return True


@periodic_task(run_every=crontab(minute='*/5'))
def start_trade_bittrex():
    exchange = Exchanges.objects.get(exchange='bittrex')
    bittrex_ue = UserExchanges.objects.filter(is_active=True, exchange=exchange)
    if len(bittrex_ue) > 0:
        for ue in bittrex_ue:
            totalBtc = float(0)
            try:
                ue_apisecret = ue.apisecret.encode()
                driver = bittrex_driver.Bittrex(api_secret=ue_apisecret, api_key=ue.apikey)
                try:
                    balances = driver.get_balances()
                    if balances['result'] is not None:
                        for c in balances['result']:
                            try:
                                user_coin = UserBalance.objects.get(ue=ue, coin=c['Currency'].lower())
                            except UserBalance.DoesNotExist:
                                user_coin = None
                            if user_coin is None:
                                new_user_coin = UserBalance()
                                new_user_coin.ue = ue
                                new_user_coin.coin = c['Currency'].lower()
                                new_user_coin.balance = float(c['Available'])
                                btc_value = get_btc_value(coin_name=c['Currency'].lower(), count=c['Balance'])
                                new_user_coin.btc_value = btc_value
                                totalBtc += btc_value
                                new_user_coin.save()
                            else:
                                user_coin.balance = float(c['Available'])
                                btc_value = get_btc_value(coin_name=c['Currency'].lower(), count=c['Balance'])
                                user_coin.btc_value = btc_value
                                totalBtc += btc_value
                                user_coin.save()
                except Exception as error:
                    print("Убираю накуй, неверно че-то")
                    ue.error = error
                    ue.is_active = False
                    ue.is_correct = False
                    ue.save()
                ue.total_btc = totalBtc
                ue.total_usd = get_usd_value('btc', totalBtc)
                ue.save()
            except HTTPException:
                print('Ошибка, начинаем заново')
    else:
        print("Никто не включил скрипт")
    return True


@shared_task
def get_all_coins():
    response = requests.get('https://poloniex.com/public?command=returnCurrencies').json()
    for item in response:
        try:
            coin = Coin.objects.get(short_name=item)
        except Coin.DoesNotExist:
            new_coin = Coin()
            new_coin.short_name = item
            new_coin.full_name = response[item]['name']
            new_coin.save()
    return True


def get_btc_value(coin_name=None, count=None):
    if not coin_name or not count:
        return 0
    else:
        response = requests.get('https://api.cryptonator.com/api/ticker/btc-' + coin_name.lower()).json()
        if response['success']:
            return float(count) / float(response['ticker']['price'])
        else:
            return 0


def get_usd_value(coin_name=None, count=None):
    if not coin_name or not count:
        return 0
    else:
        response = requests.get('https://api.cryptonator.com/api/ticker/usd-' + coin_name.lower()).json()
        if response['success']:
            return float(count) / float(response['ticker']['price'])
        else:
            return 0


def get_btc_value_from_btce(coin_name=None, count=None):
    if not coin_name or not count:
        return 0
    else:
        response = requests.get('https://btc-e.nz/api/3/ticker/btc_' + coin_name.lower()).json()
        if response:
            print(float(count) / float(response['btc_' + coin_name.lower()]['last']))
            return float(count) / float(response['btc_' + coin_name.lower()]['last'])
        else:
            return 0


@periodic_task(run_every=crontab(minute='*/2'))
def get_eth_wallet_history():
    wallet = Wallets.objects.get(name='ETH')
    eth_uw = UserWallet.objects.filter(wallet=wallet)
    if len(eth_uw) > 0:
        for uw in eth_uw:
            balance = requests.get(
                'https://api.etherscan.io/api?module=account&action=balance&address=' + uw.address + '&tag=latest&apikey=18NX2UFSA1SUX76FFGHAGFBWNNAWK7KDNY').json()
            if balance['status'] == str(1):
                uw.balance = balance['result']
                uw.total_usd = get_usd_value('eth', round(float(float(balance['result']) / (10 ** 18)), 8))
                uw.total_btc = get_btc_value('eth', round(float(float(balance['result']) / (10 ** 18)), 8))
                uw.save()
            history = requests.get(
                'https://api.etherscan.io/api?module=account&action=txlist&address=' + uw.address + '&startblock=0&endblock=99999999&sort=desc&apikey=18NX2UFSA1SUX76FFGHAGFBWNNAWK7KDNY').json()
            if history['status'] == str(1):
                for item in history['result']:
                    try:
                        wallet_history = WalletHistory.objects.get(hash=item['hash'], uw=uw)
                    except WalletHistory.MultipleObjectsReturned:
                        pass
                    except WalletHistory.DoesNotExist:
                        wallet_history = WalletHistory()
                        wallet_history.uw = uw
                        wallet_history.number = item['blockNumber']
                        wallet_history.date = datetime.datetime.fromtimestamp(int(item['timeStamp'])).strftime(
                            '%Y-%m-%d %H:%M:%S')
                        wallet_history.t_from = item['from']
                        wallet_history.t_to = item['to']
                        if item['to'] == uw.address:
                            wallet_history.type = 'in'
                        elif item['from'] == uw.address:
                            wallet_history.type = 'out'
                        else:
                            wallet_history.type = 'unknown'
                        wallet_history.value = item['value']
                        wallet_history.usd_value = get_usd_value('eth',
                                                                 round(float(float(item['value']) / (10 ** 18)), 8))
                        wallet_history.hash = item['hash']
                        wallet_history.block_hash = item['blockHash']
                        wallet_history.save()
        print('ok')
    else:
        print("Кошельки отсутствуют")
    return True


@periodic_task(run_every=crontab(minute='*/2'))
def get_btc_wallet_history():
    wallet = Wallets.objects.get(name='BTC')
    btc_uw = UserWallet.objects.filter(wallet=wallet)
    if len(btc_uw) > 0:
        for uw in btc_uw:
            balance = requests.get('http://btc.blockr.io/api/v1/address/balance/' + uw.address).json()
            if balance['status'] == 'success':
                uw.balance = balance['data']['balance']
                uw.total_usd = get_usd_value('btc', balance['data']['balance'])
                uw.total_btc = balance['data']['balance']
                uw.save()
            history = requests.get(
                'http://btc.blockr.io/api/v1/address/txs/' + uw.address).json()
            if history['status'] == 'success':
                for item in history['data']['txs']:
                    try:
                        wallet_history = WalletHistory.objects.get(uw=uw, hash=item['tx'])
                    except WalletHistory.DoesNotExist:
                        tx_his = requests.get('https://btc.blockr.io/api/v1/tx/info/' + item['tx']).json()
                        if tx_his['status'] == 'success':
                            wallet_history = WalletHistory()
                            wallet_history.uw = uw
                            wallet_history.number = tx_his['data']['block']
                            wallet_history.date = tx_his['data']['time_utc']
                            if float(item['amount']) > 0:
                                t_from = ''
                                for item_from in tx_his['data']['trade']['vins']:
                                    t_from += item_from['address'] + '<br/>'
                                t_to = uw.address
                            else:
                                t_from = uw.address
                                t_to = ''
                                for item_to in tx_his['data']['trade']['vouts']:
                                    t_to += item_to['address'] + '<br/>'
                            wallet_history.t_to = t_to
                            wallet_history.t_from = t_from
                            if t_to == uw.address:
                                wallet_history.type = 'in'
                            elif t_from == uw.address:
                                wallet_history.type = 'out'
                            else:
                                wallet_history.type = 'unknown'
                            wallet_history.value = item['amount']
                            wallet_history.usd_value = get_usd_value('btc', float(item['amount']))
                            wallet_history.hash = item['tx']
                            wallet_history.block_hash = '-'
                            wallet_history.save()
        print('ok')
    else:
        print("Кошельки отсутствуют")
    return True


@periodic_task(run_every=crontab(minute='*/2'))
def get_yandex_wallet_history():
    wallet = Wallets.objects.get(name='Yandex Money')
    yandex_uw = UserWallet.objects.filter(wallet=wallet)
    if len(yandex_uw) > 0:
        for uw in yandex_uw:
            access_token = uw.access_token
            if access_token is not None:
                yandex_wallet_object = Wallet(access_token)
                get_yandex_records(wallet=yandex_wallet_object, uw=uw)
        print('ok')
    else:
        print("Кошельки отсутствуют")
    return True


def get_yandex_records(wallet=None, uw=None, next_record=0):
    transactions = wallet.operation_history(
        {'start_record': int(next_record),
         'details': 'true',
         'records': 100})
    for t in transactions['operations']:
        try:
            wallet_history = WalletHistory.objects.get(uw=uw, number=t['operation_id'])
        except WalletHistory.DoesNotExist:
            new_wallet_history = WalletHistory()
            new_wallet_history.uw = uw
            new_wallet_history.number = t['operation_id']
            new_wallet_history.date = t['datetime']
            new_wallet_history.type = t['direction']
            new_wallet_history.t_from = new_wallet_history.t_to = '-'
            if 'details' in t:
                if len(t['details']) > 0:
                    new_wallet_history.hash = t['details']
                elif 'title' in t:
                    new_wallet_history.hash = t['title']
            elif 'title' in t:
                new_wallet_history.hash = t['title']
            new_wallet_history.value = t['amount']
            new_wallet_history.usd_value = get_usd_value('rur', float(t['amount']))
            new_wallet_history.save()
    try:
        next_rec = transactions['next_record']
    except KeyError:
        next_rec = None
    if next_rec is not None:
        get_yandex_records(wallet, uw=uw, next_record=transactions['next_record'])


@periodic_task(run_every=crontab(minute='*/1'))
def calculate_holdings_history():
    users = User.objects.all()
    for user in users:
        wallets = UserWallet.objects.filter(user=user)
        if len(wallets) > 0:
            for wallet in wallets:
                holdings = UserHoldings()
                holdings.user = user
                holdings.type = 'Wallet@' + wallet.wallet.name
                holdings.total_btc = wallet.total_btc
                holdings.total_usd = wallet.total_usd
                holdings.save()
        exchanges = UserExchanges.objects.filter(user=user)
        if len(exchanges) > 0:
            for exchange in exchanges:
                holdings = UserHoldings()
                holdings.user = user
                holdings.type = 'Exchange@' + exchange.exchange.exchange
                holdings.total_btc = exchange.total_btc
                holdings.total_usd = exchange.total_usd
                holdings.save()
    return True
