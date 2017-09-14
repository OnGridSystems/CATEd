from django.contrib import admin

from monitoring.models import *


class WorkerAdmin(admin.ModelAdmin):
    list_display = ['name', 'last_update', 'reported_hash_rate', 'address_pool']
    list_filter = ['address_pool']

    class Meta:
        model = Worker


class UserPoolsAdmin(admin.ModelAdmin):
    list_display = ['name', 'pool', 'address', 'comment', 'claymore_port']

    class Meta:
        model = UserPools


def worker_name(worker_history):
    return worker_history.worker.name


def pool(worker_history):
    if worker_history.worker.address_pool is None:
        return ''
    else:
        return worker_history.worker.address_pool.name


class WorkersHistoryAdmin(admin.ModelAdmin):
    list_display = [worker_name, pool, 'reported_hash_rate', 'sum_hr_base', 'sum_hr_base', 'date_time']
    list_filter = ['worker__name', 'worker__address_pool__name']
    ordering = ['date_time', 'worker__name']
    class Meta:
        model = WorkersHistory


admin.site.register(Worker, WorkerAdmin)
admin.site.register(Pools)
admin.site.register(UserPools, UserPoolsAdmin)
admin.site.register(WorkersHistory, WorkersHistoryAdmin)
