import datetime
from django.db.models import Sum, Count
from telebot import types
from django.core.management.base import BaseCommand, CommandError
from monitoring.models import *
import telebot


# from monitoring.models import Worker

token = '365184875:AAG5XwC7wSW1ZobwkZxrtlqpSyUb_xa5nAc'

bot = telebot.TeleBot(token)


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
                           '\r\n' + '\r\n'
        bot.send_message(message.chat.id, sendtext)

    if com == '/pools_info':

        pools = UserPools.objects.all()
        sendtext = ''
        for i in pools:
            total_hash_pool = Worker.objects.filter(address_pool=i).aggregate(Sum('reported_hash_rate'))['reported_hash_rate__sum']
            total_hash_claymore_base = Worker.objects.filter(address_pool=i).aggregate(Sum('sum_hr_base'))['sum_hr_base__sum']
            amount_workers = Worker.objects.filter(address_pool=i).filter(reported_hash_rate__gt=0).aggregate(Count('name'))['name__count']
            sendtext = sendtext + i.name + '\r\n' +\
                       'Address: ' + i.address + ':\r\n' +\
                       'Active workers: ' + str(amount_workers) + ';\r\n' + \
                       'Pool Hashrate: ' + str(total_hash_pool) + 'Mh/s;\r\n' + \
                       'Claymore Hashrate: ' + str(total_hash_claymore_base) + 'Mh/s' + \
                       '\r\n' + '\r\n'
        bot.send_message(message.chat.id, sendtext)

    if com == '/pools_details':

        pools = UserPools.objects.all()
        markup = types.ReplyKeyboardMarkup()
        for i in pools:
            markup.row(i.name)
        bot.send_message(message.chat.id, "Choose pool: ", reply_markup=markup)

    if com == '/workers':
        workers = Worker.objects.values('name').distinct().order_by('name')
        sendtext = ''
        for i in workers:
            sendtext = sendtext + i['name'] + \
                       '\r\n' + '\r\n'
        bot.send_message(message.chat.id, sendtext)

    if com == '/workers_info':
        workers = Worker.objects.all().order_by('address_pool__name', 'name')
        sendtext = ''
        for i in workers:
            sendtext = sendtext + i.name + '\r\n' + \
                       'Pools: ' + str(i.pools) + '\r\n' + \
                       'Base HR: ' + str(i.sum_hr_base) + 'Mh/s;\r\n' + \
                       'Sec HR: ' + str(i.sum_hr_sec) + 'Mh/s;\r\n' + \
                       'Claymore uptime: ' + str(datetime.timedelta(minutes=i.claymore_uptime)) + \
                       '\r\n' + '\r\n'
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