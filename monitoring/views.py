import json

import time
from django.http import HttpResponse
from django.shortcuts import render

from monitoring.models import Worker, UserPools, WorkersHistory


def monitor(request):
    args = {'pools': UserPools.objects.all()}
    return render(request, 'monitoring/pools.html', args)


def get_holding(request):
    type_r = request.GET.get('type')
    if request.is_ajax():
        if type_r == 'names':
            names = []
            pool_names = UserPools.objects.values('name').distinct()
            if len(pool_names) > 0:
                for name in pool_names:
                    names.append(name['name'])
                return HttpResponse(json.dumps(names), status=200)
            else:
                return HttpResponse('none', status=200)
        else:
            total_hash_pool = []
            date_times = WorkersHistory.objects.values('date_time').distinct()
            for dt in date_times:
                workers = WorkersHistory.objects.filter(worker__address_pool__name=type_r, date_time=dt['date_time'])
                total_hash_workers = float(0)
                for worker in workers:
                    total_hash_workers += float(worker.reported_hash_rate)
                total_hash_pool.append([int(time.mktime(dt['date_time'].timetuple()) * 1000), total_hash_workers])
            # list_hold = [obj.as_list() for obj in workers]
            return HttpResponse(json.dumps(total_hash_pool), status=200)
