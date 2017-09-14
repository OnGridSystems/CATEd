# Create your tasks here
from __future__ import absolute_import, unicode_literals

import datetime
from json import JSONDecodeError

from celery import shared_task
from celery.schedules import crontab
from celery.task import periodic_task
from django.db.models import Q
from django.shortcuts import render
import requests
import time
import re
import paramiko
import json
import subprocess
from paramiko.ssh_exception import NoValidConnectionsError
import socket
from monitoring.models import *


@periodic_task(run_every=crontab(minute='*/5'))
# @shared_task
def check_ethermine():
    pool, c = Pools.objects.get_or_create(pool='ethermine')
    address_pool = UserPools.objects.filter(pool=pool)
    if len(address_pool) > 0:
        for ap in address_pool:
            try:
                response = requests.get('https://ethermine.org/api/miner_new/' + ap.address).json()
            except JSONDecodeError:
                continue
            workers = response['workers']
            for worker in workers:
                name = workers[worker]['worker']
                last_submit_time = datetime.datetime.fromtimestamp(workers[worker]['workerLastSubmitTime'])
                reported_hash_rate = re.sub(r'[^0-9.]', '', workers[worker]['reportedHashRate'])
                valid_shares = workers[worker]['validShares']
                invalid_shares = workers[worker]['invalidShares']
                stale_shares = workers[worker]['staleShares']
                invalid_share_ratio = workers[worker]['invalidShareRatio']
                try:
                    old_worker = Worker.objects.get(Q(name=name) & (Q(address_pool=ap) | Q(address_pool__isnull=True)))
                    old_worker.last_submit_time = last_submit_time
                    old_worker.reported_hash_rate = reported_hash_rate
                    old_worker.valid_shares = valid_shares
                    old_worker.invalid_shares = invalid_shares
                    old_worker.stale_shares = stale_shares
                    old_worker.invalid_share_ratio = invalid_share_ratio
                    old_worker.address_pool = ap
                    old_worker.save()
                # TODO обновить информацию по уже существующему Воркеру
                except Worker.DoesNotExist:
                    print('Новый воркер')
                    new_worker = Worker()
                    new_worker.address_pool = ap
                    new_worker.name = worker
                    new_worker.last_submit_time = last_submit_time
                    new_worker.reported_hash_rate = reported_hash_rate
                    new_worker.valid_shares = valid_shares
                    new_worker.invalid_shares = invalid_shares
                    new_worker.stale_shares = stale_shares
                    new_worker.invalid_share_ratio = invalid_share_ratio
                    new_worker.save()
    return True


@periodic_task(run_every=crontab(minute='*/5'))
#  @shared_task
def check_nanopool():
    pool, c = Pools.objects.get_or_create(pool='nanopool')
    address_pool = UserPools.objects.filter(pool=pool)
    if len(address_pool) > 0:
        for ap in address_pool:
            try:
                response = requests.get('https://api.nanopool.org/v1/etc/reportedhashrates/' + ap.address).json()
            except JSONDecodeError:
                continue
            workers = response['data']
            for worker in workers:
                name = worker['worker']
                reported_hash_rate = worker['hashrate']
                try:
                    old_worker = Worker.objects.get(Q(name=name) & (Q(address_pool=ap) | Q(address_pool__isnull=True)))
                    old_worker.reported_hash_rate = reported_hash_rate
                    old_worker.save()
                # TODO обновить информацию по уже существующему Воркеру
                except Worker.DoesNotExist:
                    new_worker = Worker()
                    new_worker.address_pool = ap
                    new_worker.name = name
                    new_worker.reported_hash_rate = reported_hash_rate
                    new_worker.save()
    return True


@periodic_task(run_every=crontab(minute='*/5'))
def save_worker_history():
    date = datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S')
    workers = Worker.objects.all()
    for worker in workers:
        new_worker_history = WorkersHistory()
        new_worker_history.worker = worker
        new_worker_history.date_time = date
        new_worker_history.reported_hash_rate = worker.reported_hash_rate
        new_worker_history.sum_hr_base = worker.sum_hr_base
        new_worker_history.sum_hr_sec = worker.sum_hr_sec
        new_worker_history.save()
    return True


@periodic_task(run_every=crontab(minute='*/5'))
# @shared_task
def uptime_worker():
    f = open('/etc/hosts', 'r')
    arr = []
    for line in f:
        if line.startswith('192'):
            ip = line.split()[0]
            m = re.match(r'^([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})$', ip)
            if 100 < int(m.group(4)) < 199:
                arr.append(line.split())

    for i in range(len(arr)):
        rigip = str(arr[i][0])
        # print(arr[i][1])
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # print(Worker.objects.filter(name=arr[i][1]).values("uptime"))
        try:
            ssh.connect(rigip, username='user', password='123-qwe')
            rigcomm = "awk '{print int($1)}' /proc/uptime"
            stdin, stdout, stderr = ssh.exec_command(rigcomm)
            name = arr[i][1]
            uptime = stdout.read().decode('utf-8')
            worker = Worker.objects.filter(name=name)
            if len(worker) > 0:
                for w in worker:
                    w.uptime = uptime
                    w.ip_address = rigip
                    w.save()
            else:
                new_worker = Worker()
                new_worker.name = name
                new_worker.uptime = uptime
                new_worker.ip_address = rigip
                new_worker.save()
        except NoValidConnectionsError:
            # print(rigip + ' не найден')
            pass
    return True


@periodic_task(run_every=crontab(minute='*/5'))
# @shared_task
def check_claymore():
    workers = Worker.objects.all()
    for worker in workers:
        # ip = worker.ip_address
        # if worker.address_pool is not None:
        #     port = str(worker.address_pool.claymore_port)
        # else:
        #     port = '3333'
        # id = '{"id":0,"jsonrpc":"2.0","method":"miner_getstat1"}'
        # # print(port)
        # rigcomm = "echo '"+id+"' | netcat '"+ ip + "' '" + port + "'"
        # PIPE = subprocess.PIPE
        # t = subprocess.Popen(rigcomm, shell=True, stdin=PIPE, stdout=PIPE,
        #                  stderr=subprocess.STDOUT, close_fds=True, cwd='/home/')
        # c=t.stdout.read()
        HOST = worker.ip_address
        if worker.address_pool is not None:
            PORT = worker.address_pool.claymore_port
        else:
            PORT = 3333
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((HOST, PORT))
                s.sendall(b'{"id":0,"jsonrpc":"2.0","method":"miner_getstat1"}')
                data = s.recv(1024)
            except Exception:
                continue

        # весь массив, возвращённый c клэймора
        returned = json.loads(data.decode("utf-8"))['result']
        # print(returned)

        claymore_version = returned[0].split(';')[0]
        # print(claymore_version)

        claymore_uptime = returned[1].split(';')[0]
        # print(claymore_uptime)

        hr_base = returned[3].split(';')

        sum_hr_base = round(sum([float(int(i) / 1000) for i in hr_base]), 3)
        hr_details_base = '; '.join([str(int(hr_base[i]) / 1000) + 'Mh/s' for i in range(len(hr_base))])
        # print(sum_hr_base)
        # print(hr_details_base)

        hr_sec = returned[5].split(';')
        if hr_sec[0] != 'off':
            sum_hr_sec = round(sum([float(int(i) / 1000) for i in hr_sec]), 3)
            hr_details_sec = '; '.join([str(int(hr_sec[i]) / 1000) + 'Mh/s' for i in range(len(hr_sec))])
        else:
            sum_hr_sec = 0
            hr_details_sec = ''
        # print(sum_hr_sec)
        # print(hr_details_sec)

        cooling = returned[6].split(';')
        temperature, fun_speed = '; '.join([str(cooling[i]) + 'C' for i in range(len(cooling)) if i % 2 == 0]), \
                                 '; '.join([str(cooling[i]) + '%' for i in range(len(cooling)) if i % 2 != 0])
        # print(temperature)
        # print(fun_speed)

        pools = str(returned[7]).replace(';', '; ')
        # print(pools)
        worker.claymore_version = claymore_version
        worker.claymore_uptime = claymore_uptime
        worker.sum_hr_base = sum_hr_base
        worker.hr_details_base = hr_details_base
        worker.sum_hr_sec = sum_hr_sec
        worker.hr_details_sec = hr_details_sec
        worker.temperature = temperature
        worker.fun_speed = fun_speed
        worker.pools = pools
        worker.save()

    workers = Worker.objects.filter(last_update__lt=(datetime.datetime.now() - datetime.timedelta(minutes=5)))
    for worker in workers:
        worker.claymore_version = 'offline'
        worker.claymore_uptime = 0
        worker.sum_hr_base = 0
        worker.hr_details_base = None
        worker.sum_hr_sec = 0
        worker.hr_details_sec = None
        worker.temperature = 'offline'
        worker.fun_speed = 'offline'
        worker.pools = 'offline'
        worker.reported_hash_rate = 0
        worker.uptime = 0
        worker.save()
    return True
