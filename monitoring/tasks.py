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


# @periodic_task(run_every=crontab(minute='*/5'))
@shared_task
def uptime_worker():
    ssh = paramiko.SSHClient()
    privkey = paramiko.RSAKey.from_private_key_file('/home/klyaus/.ssh/id_rsa')
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('vpn.ongrid.pro', username='d.suldin', pkey=privkey)
    comm = "python3 /opt/script.py"
    print("Executing {}".format(comm))
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
            if worker is not None:
                for w in worker:
                    w.uptime = uptime
                    w.save()
            else:
                new_worker = Worker()
                new_worker.name = name
                new_worker.uptime = uptime
                new_worker.save()
        except NoValidConnectionsError:
            # print(rigip + ' не найден')
            pass
    return True
