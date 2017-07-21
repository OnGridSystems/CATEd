from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render, redirect
from trade.models import UserExchanges, Exchanges
from tradeBOT.models import UserCoin, ExchangeCoin, UserDeactivatedPairs, Pair, ExchangeMainCoin


def main(request):
    args = {'user_coins': UserCoin.objects.all()}
    return render(request, 'tradeBOT/index.html', args)


def setup(request, pk):
    # args = {'ue': UserExchanges.objects.values('exchange__exchange').filter(user=request.user).distinct()}
    args = {}
    try:
        args['user_exchange'] = UserExchanges.objects.get(pk=pk, user=request.user)
        args['coins'] = ExchangeCoin.objects.filter(exchange=args['user_exchange'].exchange).order_by('-is_active',
                                                                                                      'name')
        args['user_coins'] = UserCoin.objects.filter(user_exchange__pk=pk, user=request.user).order_by(
            '-rank')
        args['primary_coins'] = ExchangeMainCoin.objects.filter(coin__exchange=args['user_exchange'].exchange)
    except UserExchanges.DoesNotExist:
        return redirect('index')
    return render(request, 'tradeBOT/setup.html', args)


def add_user_coin(request):
    if request.method == 'POST':
        coin_pk = request.POST.get('coin')
        user_exchange_pk = request.POST.get('user-exchange')
        try:
            user_exchange = UserExchanges.objects.get(pk=user_exchange_pk)
            coin = ExchangeCoin.objects.get(pk=coin_pk)
            user_coin = UserCoin.objects.get(coin=coin, user_exchange=user_exchange)
        except ExchangeCoin.DoesNotExist:
            pass
        except UserExchanges.DoesNotExist:
            pass
        except UserCoin.DoesNotExist:
            new_user_coin = UserCoin()
            new_user_coin.coin = coin
            new_user_coin.user = request.user
            new_user_coin.user_exchange = user_exchange
            new_user_coin.save()
        return redirect('/trade/setup/' + str(user_exchange_pk) + '/')


def changerank(request):
    if request.is_ajax():
        coin_id = request.POST.get('coin_id')
        type_c = request.POST.get('type')
        try:
            user_coin = UserCoin.objects.get(pk=coin_id, user=request.user)
        except UserCoin.DoesNotExist:
            return HttpResponse('false', status=200)
        if type_c == 'up':
            user_coin.rank = user_coin.rank + 1
            user_coin.save()
        elif type_c == 'down':
            if user_coin.rank > 1:
                user_coin.rank = user_coin.rank - 1
                user_coin.save()
    return HttpResponse('ok', status=200)


def toggle_pair(request):
    if request.is_ajax():
        pair_id = request.POST.get('pair_id')
        user_exch_pk = request.POST.get('user_exch')
        try:
            pair = Pair.objects.get(pk=pair_id)
            user_exch = UserExchanges.objects.get(pk=user_exch_pk, user=request.user)
            user_deactive_pair = UserDeactivatedPairs.objects.get(pair=pair, user_exchange=user_exch).delete()
        except Pair.DoesNotExist:
            return HttpResponse('Pair doesn\'t found!', status=200)
        except UserExchanges.DoesNotExist:
            return HttpResponse('Exchange doesn\'t found!', status=200)
        except UserDeactivatedPairs.DoesNotExist:
            new_user_deactive_pair = UserDeactivatedPairs()
            new_user_deactive_pair.pair = pair
            new_user_deactive_pair.user_exchange = user_exch
            new_user_deactive_pair.save()
        return HttpResponse('ok', status=200)


def set_share(request):
    if request.is_ajax():
        user_coin_id = request.POST.get('coin_id')
        share = request.POST.get('share')
        user_exch = request.POST.get('user_exch')
        if int(share) == 0:
            try:
                user_coin = UserCoin.objects.get(pk=user_coin_id, user=request.user)
                user_coin.share = share
                user_coin.save()
            except UserCoin.DoesNotExist:
                return HttpResponse('Not your coin', status=200)
            return HttpResponse('ok', status=200)
        user_coins_share_summ = UserCoin.objects.filter(user=request.user, user_exchange__pk=user_exch).exclude(pk=user_coin_id).aggregate(Sum('share'))['share__sum']
        if user_coins_share_summ is None:
            user_coins_share_summ = 0
        if float(user_coins_share_summ) + float(share) > 100:
            return HttpResponse('Sum shares cant be more than 100', status=200)
        try:
            user_coin = UserCoin.objects.get(pk=user_coin_id, user=request.user)
            user_coin.share = share
            user_coin.save()
        except UserCoin.DoesNotExist:
            return HttpResponse('Not your coin', status=200)
        return HttpResponse('ok', status=200)


def delete_user_coin(request):
    if request.is_ajax():
        user_coin_id = request.POST.get('coin_id')
        try:
            user_coin = UserCoin.objects.get(pk=user_coin_id, user=request.user).delete()
        except UserCoin.DoesNotExist:
            return HttpResponse('Not your coin', status=200)
        return HttpResponse('ok', status=200)


def relations(request):
    args = {'exchanges': Exchanges.objects.all()}
    return render(request, 'tradeBOT/relations.html', args)


def change_user_exchange_script_activity(request):
    if request.is_ajax():
        user_exch_id = request.POST.get('user_exch')
        try:
            user_exch = UserExchanges.objects.get(pk=user_exch_id, user=request.user)
            user_exch.is_active_script = not user_exch.is_active_script
            user_exch.save()
            return HttpResponse('true', status=200)
        except UserExchanges.DoesNotExist:
            return HttpResponse('false', status=200)
