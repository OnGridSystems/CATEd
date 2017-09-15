# from slacker import Slacker
# slack = Slacker('xoxb-230633578469-NkN9fdZdoKVbgHvSbkzHOtC6')
from django.core.management.base import BaseCommand
import time
from slackclient import SlackClient
import datetime
from django.db.models import Sum, Count
from monitoring.models import *

BOT_TOKEN = "xoxb-230633578469-NkN9fdZdoKVbgHvSbkzHOtC6"
CHANNEL_NAME = "monitoring"

pools_name = list(UserPools.objects.values('name'))
workers_name = list(Worker.objects.values('name'))


def is_in(name, variable):
    for item in variable:
        if item['name'] == name:
            return True
    return False


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    # def add_arguments(self, parser):
    #     parser.add_argument('message', nargs='+', type=str)

    def handle(self, *args, **options):

        # Create the slackclient instance
        sc = SlackClient(BOT_TOKEN)

        # Connect to slack
        if sc.rtm_connect():
            # Send first message
            # sc.rtm_send_message(CHANNEL_NAME, "I'm ALIVE!!!")

            while True:
                # Read latest messages
                for slack_message in sc.rtm_read():
                    message = slack_message.get("text")
                    user = slack_message.get("user")
                    sendtext = ''
                    if not message or not user:
                        continue

                    if message == 'help':
                        sendtext = 'Доступные команды:\r\n\r\n' + \
                                   'список пулов: pools' + '\r\n\r\n' + \
                                   'информация по пулам: pools_info' + '\r\n\r\n' + \
                                   'подробности по пулу: <PoolName>' + '\r\n\r\n' + \
                                   'список ригов: workers' + '\r\n\r\n' + \
                                   'информация по ригам: workers_info' + '\r\n\r\n' + \
                                   'подробности по ригу: <WorkerName>'

                    if message == 'pools':
                        pools = UserPools.objects.all()
                        for i in pools:
                            sendtext = sendtext + i.name + \
                                       '\r\n\r\n'

                    if message == 'pools_info':
                        pools = UserPools.objects.all()
                        for i in pools:
                            total_hash_pool = \
                                Worker.objects.filter(address_pool=i).aggregate(Sum('reported_hash_rate'))[
                                    'reported_hash_rate__sum']
                            total_hash_claymore_base = \
                                Worker.objects.filter(address_pool=i).aggregate(Sum('sum_hr_base'))['sum_hr_base__sum']
                            amount_workers = \
                                Worker.objects.filter(address_pool=i).filter(reported_hash_rate__gt=0).aggregate(
                                    Count('name'))['name__count']
                            sendtext = sendtext + i.name + '\r\n' + \
                                       'Address: ' + i.address + ':\r\n' + \
                                       'Active workers: ' + str(amount_workers) + ';\r\n' + \
                                       'Pool hashrate: ' + str(total_hash_pool) + 'Mh/s;\r\n' + \
                                       'Claymore hashrate: ' + str(total_hash_claymore_base) + 'Mh/s' + \
                                       '\r\n\r\n'

                    if is_in(message, pools_name) == True:
                        pool = UserPools.objects.get(name=message)
                        total_hash_pool = \
                            Worker.objects.filter(address_pool=pool).aggregate(Sum('reported_hash_rate'))[
                                'reported_hash_rate__sum']
                        total_hash_claymore_base = \
                            Worker.objects.filter(address_pool=pool).aggregate(Sum('sum_hr_base'))['sum_hr_base__sum']
                        amount_workers = \
                            Worker.objects.filter(address_pool=pool).filter(reported_hash_rate__gt=0).aggregate(
                                Count('name'))['name__count']
                        offline_workers = \
                            Worker.objects.filter(address_pool=pool).filter(reported_hash_rate=0).aggregate(
                                Count('name'))['name__count']
                        sendtext = sendtext + pool.name + '\r\n' + \
                                   'Address: ' + pool.address + ':\r\n' + \
                                   'Active workers: ' + str(amount_workers) + ';\r\n' + \
                                   'Offline workers: ' + str(offline_workers) + ';\r\n' + \
                                   'Pool hashrate: ' + str(total_hash_pool) + 'Mh/s;\r\n' + \
                                   'Claymore hashrate: ' + str(total_hash_claymore_base) + 'Mh/s\r\n\r\n\r\n'

                        workers = Worker.objects.filter(address_pool=pool).values('name',
                                                                                  'reported_hash_rate').distinct().order_by(
                            'name')
                        for i in workers:
                            sendtext = sendtext + i['name'] + ' (' + str(i['reported_hash_rate']) + 'Mh/s' + ')' \
                                                                                                             '\r\n\r\n'

                    if message == 'workers':
                        workers = Worker.objects.values('name').distinct().order_by('name')
                        for i in workers:
                            sendtext = sendtext + i['name'] + \
                                       '\r\n\r\n'

                    if message == 'workers_info':
                        workers = Worker.objects.all().order_by('address_pool__name', 'name')
                        for i in workers:
                            sendtext = sendtext + i.name + '\r\n' + \
                                       'Pools: ' + str(i.pools) + '\r\n' + \
                                       'Claymore base hashrate: ' + str(i.sum_hr_base) + 'Mh/s;\r\n' + \
                                       'Claymore sec hashrate: ' + str(i.sum_hr_sec) + 'Mh/s;\r\n' + \
                                       'Pool hashrate: ' + str(i.reported_hash_rate) + 'Mh/s;\r\n' + \
                                       'Claymore uptime: ' + str(datetime.timedelta(minutes=i.claymore_uptime)) + \
                                       '\r\n\r\n'

                    if is_in(message, workers_name) == True:
                        worker = Worker.objects.filter(name=message)
                        for i in worker:
                            if i.sum_hr_base == 0 and i.reported_hash_rate == 0:
                                sendtext = sendtext + i.name + ' OFFLINE'
                            else:
                                sendtext = sendtext + i.name + '\r\n' + \
                                           'Pools: ' + str(i.pools) + '\r\n' + \
                                           'Base pool name: ' + i.address_pool.name + '\r\n' + \
                                           'Pool hashrate: ' + str(i.reported_hash_rate) + 'Mh/s;\r\n' + \
                                           'Claymore base hashrate: ' + str(
                                    i.sum_hr_base) + 'Mh/s ' + '(' + i.hr_details_base + ');\r\n' + \
                                           'Claymore sec hashrate: ' + str(
                                    i.sum_hr_sec) + 'Mh/s ' + '(' + i.hr_details_sec + ');\r\n' + \
                                           'Temperatures: ' + i.temperature + ';\r\n' + \
                                           'Fun speed: ' + i.fun_speed + ';\r\n' + \
                                           'System uptime: ' + str(datetime.timedelta(seconds=i.uptime)) + ';\r\n' + \
                                           'Claymore uptime: ' + str(
                                    datetime.timedelta(minutes=i.claymore_uptime)) + '\r\n' + \
                                           'Version: ' + i.claymore_version + \
                                           '\r\n\r\n'

                    sc.rtm_send_message(CHANNEL_NAME, "<@{}> ".format(user) + '\r\n' + sendtext)
                # Sleep for half a second
                time.sleep(0.5)
