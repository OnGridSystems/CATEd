from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from .models import ExchangeTicker
from django.utils import timezone
import datetime
from tradeBOT.models import Extremum
import json


def get_ticker(request):
    if request.is_ajax():
        pair_id = request.POST.get('pair_id')
        intervale = int(request.POST.get('intervale'))
        zoom = request.POST.get('zoom')
        chart_data = {}
        ticker_list = []
        extremums_list = []
        intervales = []
        if zoom == 'all':
            ticker = list(ExchangeTicker.objects.values('date_time', 'last').filter(pair_id=pair_id))
        else:
            ticker = list(ExchangeTicker.objects.values('date_time', 'last').filter(pair_id=pair_id,
                                                                                    date_time__gte=timezone.now() - datetime.timedelta(
                                                                                        hours=int(zoom))))
        if len(ticker) > 0:
            extremums = Extremum.objects.filter(pair_id=pair_id,
                                                date__gte=ticker[0]['date_time'])
            for item in extremums:
                extremums_list.append([item.date, item.price, item.ext_type])
            s_date = ticker[0]['date_time']
            while s_date < timezone.now():
                intervales.append(s_date)
                s_date = s_date + datetime.timedelta(minutes=intervale)
            if len(intervales) > 0:
                s_date = intervales.pop(0)
                # print('От {} до {}'.format(s_date, s_date + datetime.timedelta(minutes=intervale)))
                s_chain = [x for x in ticker if
                           s_date + datetime.timedelta(minutes=intervale) > x['date_time'] >= s_date]
                while len(intervales) > 0:
                    try:
                        ticker_list.append({'date': s_date,
                                            'open': s_chain[0]['last'],
                                            'close': s_chain[-1]['last'],
                                            'low': min([x['last'] for x in s_chain]),
                                            'high': max([x['last'] for x in s_chain])})
                    except IndexError:
                        pass
                    s_date = intervales.pop(0)
                    # print('Новая от {} до {}'.format(s_date, s_date + datetime.timedelta(minutes=intervale)))
                    s_chain = [x for x in ticker if
                               s_date + datetime.timedelta(minutes=intervale) > x['date_time'] >= s_date]
                    # print("Выборка {}".format(s_chain))
        chart_data['ticker'] = ticker_list
        chart_data['extremums'] = extremums_list
        return HttpResponse(json.dumps(chart_data, cls=DjangoJSONEncoder), status=200)
