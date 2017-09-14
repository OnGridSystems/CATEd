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
                        sendtext = 'Доступные команды:\r\n' + \
                                   'список пулов: pools' + '\r\n' + \
                                   'информация по пулам: pools_info' + '\r\n' + \
                                    'подробности по пулам: <PoolName>_details' + '\r\n' + \
                                   'список ригов: workers' + '\r\n' + \
                                   'информация по ригам: workers_info' + '\r\n' + \
                                    'подробности по ригам: <WorkerName>_details'

                    if message == 'pools':
                        pools = UserPools.objects.all()
                        for i in pools:
                            sendtext = sendtext + i.name + \
                                       '\r\n' + '\r\n'

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
                                       'Pool Hashrate: ' + str(total_hash_pool) + 'Mh/s;\r\n' + \
                                       'Claymore Hashrate: ' + str(total_hash_claymore_base) + 'Mh/s' + \
                                       '\r\n' + '\r\n'

                    if message == 'workers':
                        workers = Worker.objects.values('name').distinct().order_by('name')
                        for i in workers:
                            sendtext = sendtext + i['name'] + \
                                       '\r\n' + '\r\n'

                    if message == 'workers_info':
                        workers = Worker.objects.all().order_by('address_pool__name', 'name')
                        for i in workers:
                            sendtext = sendtext + i.name + '\r\n' + \
                                       'Pools: ' + str(i.pools) + '\r\n' + \
                                        'Base HR: ' + str(i.sum_hr_base) + 'Mh/s;\r\n' + \
                                        'Sec HR: ' + str(i.sum_hr_sec) + 'Mh/s;\r\n' + \
                                        'Claymore uptime: ' + str(datetime.timedelta(minutes=i.claymore_uptime)) + \
                                        '\r\n' + '\r\n'
                    sc.rtm_send_message(CHANNEL_NAME, "<@{}> ".format(user) + '\r\n' + sendtext)
                # Sleep for half a second
                time.sleep(0.5)