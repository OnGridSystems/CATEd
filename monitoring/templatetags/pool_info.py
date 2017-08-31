from django import template
from django.db.models import Sum, Count

from monitoring.models import *
import datetime

register = template.Library()


@register.inclusion_tag('monitoring/pools.html')
def get_pools():
    pools = UserPools.objects.all()
    return {'pools': pools}


@register.inclusion_tag('monitoring/pool_workers.html')
def get_pool_workers(user_pool):
    workers = Worker.objects.filter(address_pool=user_pool)
    return {'workers': workers}


@register.inclusion_tag('monitoring/claymore_workers.html')
def get_claymore_workers():
    workers = Worker.objects.all().order_by('name')
    return {'workers': workers}


@register.filter(name='pool_total_hash')
def pool_total_hash(user_pool):
    total = Worker.objects.filter(
        address_pool=user_pool).aggregate(
        Sum('reported_hash_rate'))['reported_hash_rate__sum']
    return total


@register.filter(name='amount_workers')
def amount_workers(user_pool):
    amount = Worker.objects.filter(
        address_pool=user_pool).filter(
        reported_hash_rate__gt=0).aggregate(
        Count('name'))['name__count']
    return amount


@register.filter(name='worker_uptime')
def worker_uptime(i):
    uptime = str(datetime.timedelta(seconds=i))
    return uptime


@register.filter(name='claymore_uptime')
def claymore_uptime(i):
    uptime = str(datetime.timedelta(minutes=i))
    return uptime
