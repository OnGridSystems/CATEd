# Create your tasks here
from __future__ import absolute_import, unicode_literals

import datetime
from celery import shared_task
from celery.schedules import crontab
from celery.task import periodic_task
from django.shortcuts import render
import requests
import time
import re
import paramiko
import json
import subprocess
from paramiko.ssh_exception import NoValidConnectionsError

from monitoring.models import *


@periodic_task(run_every=crontab(minute='*/5'))
# @shared_task
def check_ethermine():
    pool = Pools.objects.get(pool='ethermine')
    address_pool = UserPools.objects.filter(pool=pool)
    if len(address_pool) > 0:
        for ap in address_pool:
            response = requests.get('https://ethermine.org/api/miner_new/' + ap.address).json()
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
                    old_worker = Worker.objects.get(name=worker, address_pool=ap)
                    old_worker.last_submit_time = last_submit_time
                    old_worker.reported_hash_rate = reported_hash_rate
                    old_worker.valid_shares = valid_shares
                    old_worker.invalid_shares = invalid_shares
                    old_worker.stale_shares = stale_shares
                    old_worker.invalid_share_ratio = invalid_share_ratio
                    old_worker.save()
                # TODO обновить информацию по уже существующему Воркеру
                except Worker.DoesNotExist:
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
# @shared_task
def check_nanopool():
    pool = Pools.objects.get(pool='nanopool')
    address_pool = UserPools.objects.filter(pool=pool)
    if len(address_pool) > 0:
        for ap in address_pool:
            response = requests.get('https://api.nanopool.org/v1/etc/reportedhashrates/' + ap.address).json()
            workers = response['data']
            for worker in workers:
                name = worker['worker']
                reported_hash_rate = worker['hashrate']
                try:
                    old_worker = Worker.objects.get(name=name, address_pool=ap)
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
        new_worker_history.save()
    return True


@periodic_task(run_every=crontab(minute='*/5'))
# @shared_task
def uptime_worker():
    ssh = paramiko.SSHClient()
    privkey = paramiko.RSAKey.from_private_key_file('/home/klyaus/.ssh/id_rsa')
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('vpn.ongrid.pro', username='d.suldin', pkey=privkey)
    comm = "python3 /opt/script.py"
    # print("Executing {}".format(comm))
    stdin, stdout, stderr = ssh.exec_command(comm)
    h = json.loads(stdout.read().decode('utf-8'))
    for i in range(len(h)):
        rigip = str(h[i][0])
        print(h[i][1])
        print(Worker.objects.filter(name=h[i][1]).values("uptime"))
        try:
            ssh.connect(rigip, username='user', pkey=privkey)
            rigcomm = "awk '{print int($1)}' /proc/uptime"
            stdin, stdout, stderr = ssh.exec_command(rigcomm)
            name = h[i][1]
            uptime = stdout.read().decode('utf-8')
            worker = Worker.objects.filter(name=name)
            if len(worker)>0:
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
        ip = worker.ip_address
        if worker.address_pool is not None:
            port = str(worker.address_pool.claymore_port)
        else:
            port = '3333'
        id = '{"id":0,"jsonrpc":"2.0","method":"miner_getstat1"}'
        # print(port)
        rigcomm = "echo '"+id+"' | netcat '"+ ip + "' '" + port + "'"
        PIPE = subprocess.PIPE
        t = subprocess.Popen(rigcomm, shell=True, stdin=PIPE, stdout=PIPE,
                         stderr=subprocess.STDOUT, close_fds=True, cwd='/home/')

        c=t.stdout.read()

        # весь массив, возвращённый c клэймора
        returned = json.loads(c.decode("utf-8"))['result']
        # print(returned)

        claymore_version=returned[0].split(';')[0]
        # print(claymore_version)

        claymore_uptime = returned[1].split(';')[0]
        # print(claymore_uptime)

        hr_base = returned[3].split(';')

        sum_hr_base = round(sum([float(int(i) / 1000) for i in hr_base]), 3)
        hr_details_base = '; '.join([str(int(hr_base[i])/1000) + 'Mh/s' for i in range(len(hr_base))])
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

        pools = str(returned[7]).replace(';','; ')
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
    return True