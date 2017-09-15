from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from kombu import Queue, Exchange

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoTrade.settings')
app = Celery('djangoTrade')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.conf.task_queues = {
    Queue('high', Exchange('high'), routing_key='high'),
    Queue('normal', Exchange('normal'), routing_key='normal'),
    Queue('low', Exchange('low'), routing_key='low'),
    Queue('set_orders', Exchange('set_orders'), routing_key='set_orders'),
}
app.conf.task_default_queue = 'normal'
app.conf.task_default_exchange_type = 'direct'
app.conf.task_default_routing_key = 'normal'


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))