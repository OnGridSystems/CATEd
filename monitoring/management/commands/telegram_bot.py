import datetime
from django.db.models import Sum, Count
from telebot import types
from django.core.management.base import BaseCommand, CommandError
from monitoring.models import *
import telebot

# from monitoring.models import Worker

token = '365184875:AAG5XwC7wSW1ZobwkZxrtlqpSyUb_xa5nAc'

bot = telebot.TeleBot(token)

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
        bot.polling(none_stop=True)


# 240111655
# Обработчик команд '/start' и '/help'.
@bot.message_handler(commands=['help'])
def handle_help(message):
    markup = types.ReplyKeyboardMarkup()
    markup.row('/pools')
    markup.row('/pools_info')
    markup.row('/pools_details')
    markup.row('/workers')
    markup.row('/workers_info')
    markup.row('/worker_details')
    # sendtext = ''
    bot.send_message(message.chat.id, "Commands:", reply_markup=markup)
    pass


@bot.message_handler(content_types=["text"])
def new_message(message):  # Название функции не играет никакой роли, в принципе
    workers = Worker.objects.filter(last_update__lt=(datetime.datetime.now() - datetime.timedelta(minutes=5)))
    for i in workers:
        print(i.name)
    print(datetime.datetime.now() - datetime.timedelta(minutes=5))
    com = message.text
    print(com)


    if com == '/pools':

        pools = UserPools.objects.all()
        sendtext = ''
        for i in pools:
            sendtext = sendtext + i.name + \
                       '\r\n\r\n'
        bot.send_message(message.chat.id, sendtext)


    if com == '/pools_info':

        pools = UserPools.objects.all()
        sendtext = ''
        for i in pools:
            total_hash_pool = Worker.objects.filter(address_pool=i).aggregate(Sum('reported_hash_rate'))[
                'reported_hash_rate__sum']
            total_hash_claymore_base = Worker.objects.filter(address_pool=i).aggregate(Sum('sum_hr_base'))[
                'sum_hr_base__sum']
            amount_workers = \
            Worker.objects.filter(address_pool=i).filter(reported_hash_rate__gt=0).aggregate(Count('name'))[
                'name__count']
            sendtext = sendtext + i.name + '\r\n' + \
                       'Address: ' + i.address + ':\r\n' + \
                       'Active workers: ' + str(amount_workers) + ';\r\n' + \
                       'Pool hashrate: ' + str(total_hash_pool) + 'Mh/s;\r\n' + \
                       'Claymore hashrate: ' + str(total_hash_claymore_base) + 'Mh/s' + \
                       '\r\n\r\n'
        bot.send_message(message.chat.id, sendtext)


    if com == '/pools_details':

        pools = UserPools.objects.all()
        markup = types.ReplyKeyboardMarkup()
        for i in pools:
            markup.row(i.name)
        bot.send_message(message.chat.id, "Choose pool: ", reply_markup=markup)


    if is_in(com, pools_name) == True:

        pool = UserPools.objects.get(name=com)
        sendtext = ''
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
        bot.send_message(message.chat.id, sendtext)

        markup = types.ReplyKeyboardMarkup()
        markup.row('/pools')
        markup.row('/pools_info')
        markup.row('/pools_details')
        markup.row('/workers')
        markup.row('/workers_info')
        markup.row('/worker_details')
        # sendtext = ''


    if com == '/workers':

        workers = Worker.objects.values('name').distinct().order_by('name')
        sendtext = ''
        for i in workers:
            sendtext = sendtext + i['name'] + \
                       '\r\n\r\n'
        bot.send_message(message.chat.id, sendtext)


    if com == '/workers_info':

        workers = Worker.objects.all().order_by('address_pool__name', 'name')
        sendtext = ''
        for i in workers:
            sendtext = sendtext + i.name + '\r\n' + \
                       'Pools: ' + str(i.pools) + '\r\n' + \
                       'Claymore base hashrate: ' + str(i.sum_hr_base) + 'Mh/s;\r\n' + \
                       'Claymore sec hashrate: ' + str(i.sum_hr_sec) + 'Mh/s;\r\n' + \
                       'Pool hashrate: ' + str(i.reported_hash_rate) + 'Mh/s;\r\n' + \
                       'Claymore uptime: ' + str(datetime.timedelta(minutes=i.claymore_uptime)) + \
                       '\r\n\r\n'
        bot.send_message(message.chat.id, sendtext)


    if com == '/worker_details':

        workers = Worker.objects.values('name').distinct().order_by('name')
        markup = types.ReplyKeyboardMarkup()
        for i in workers:
            markup.row(i['name'])
        bot.send_message(message.chat.id, "Choose rig: ", reply_markup=markup)

    if is_in(com, workers_name) == True:
        worker = Worker.objects.filter(name=com)
        sendtext = ''
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
        bot.send_message(message.chat.id, sendtext)


    if com == 'список_пулов':
        pools = UserPools.objects.all()
        sendtext = ''
        markup = types.ReplyKeyboardMarkup()
        for i in pools:
            # sendtext = i.name + ' ' + i.address
            markup.row(i.name + ' ' + i.address)
            # sendtext = 'sdsdsd'
            print(sendtext)
        bot.send_message(message.chat.id, "выбери пул: ", reply_markup=markup)

    if com == 'список_ригов':
        workers = Worker.objects.all()
        sendtext = ''
        markup = types.ReplyKeyboardMarkup()
        for i in workers:
            sendtext = i.name
            # sendtext = 'sdsdsd'
            print(sendtext)
            markup.row(i.name)
        bot.send_message(message.chat.id, "выбери риг: ", reply_markup=markup)
        # worker = Worker.objects.get(name=com)
        # sendtext = worker.sum_hr_base
        #
        # bot.send_message(message.chat.id, sendtext)
        # markup = types.ReplyKeyboardMarkup()
        # markup.row('эти', 'сверху')
        # markup.row('эти', 'всередине')
        # markup.row('эти', 'снизу')
        # bot.send_message(message.chat.id, "Клацни ёпт:", reply_markup=markup)

        # print(bot)
        # print(message)

        #
        #  if __name__ == '__main__':
        #
