[![OnGrid Systems Blockchain Applications DApps Development](images/ongrid-systems-cover.png)](https://ongrid.pro/)

![GitHub last commit](https://img.shields.io/github/last-commit/robotveradev/VeraWebApp.svg)
![GitHub release](https://img.shields.io/github/release/robotveradev/VeraWebApp.svg)
[![Project website](https://img.shields.io/website-up-down-green-red/http/vera.jobs.svg?label=project-site)](https://vera.jobs)
[![Demo website](https://img.shields.io/website-up-down-green-red/http/demo.vera.jobs.svg?label=demo-site)](https://vera.wtf)
![License](https://img.shields.io/github/license/robotveradev/VeraWebApp.svg)


# CATEd - Cryptocurrency Analytics and Trading Engine for Django

## Overview

[HabraHabr article in Russian](https://habrahabr.ru/users/proofx/posts/)

CATEd is the cryptocurrency trading bot written on Python 3 with feature-rich management Web interface (Django, Celery).

Main features:
* View the status of exchange accounts, transactions and orders on them;
* View the status of cold wallets and transactions details;
* History of deposits and withdrawals on graphical diagram;
* Configurable buy/sell/hold logic, (allowed tokens and proportions);
* Keeping the balances of different tokens at the configured levels;

![home_page](https://github.com/OnGridSystems/CATEd/blob/master/images/home_page.jpg)

![main_bot_page](https://github.com/OnGridSystems/CATEd/blob/master/images/final_screen.jpg)

## Install

You need python3, mysql-server, rabbitmq-server and redis-server to be installed.

Create python virtual env and activate it in your favorite way.

Clone project
```sh
git clone git@github.com:OnGridSystems/CATEd.git
```
Go to project dir
```sh
cd CATEd
```
Create mysql databases
```sh
echo "create database trade character set utf8; create database celery_result; create database portal_ticker;" | mysql -u root
```
And migrate
```sh
python manage.py migrate
```
Load initial data with some exchanges and wallets
```sh
python manage.py loaddata dump.json
```

Create you own superuser with
```sh
python manage.py createsuperuser
```
Before starting the bot should read the list of currencies from the site coinmarketcup.com. To do this run following code
with activated virtual environment.
```sh 
read -d "" PYTASKS <<"EOF"
from tradeBOT import tasks
coinmarketcup = tasks.pull_coinmarketcup()
EOF
echo "$PYTASKS" | python manage.py shell
```
And runserver
```sh 
python manage.py runserver
```
Now you can add your api keys.

**Add NEW api keys for use bot.**

To do this open http://127.0.0.1:8000/ in your browser, login and click red "plus" button in the lower right corner.

Bot uses several celery queues for trade, and main is triggered by a signal from a first worker named celery@worker_high.
Another worker - worker_set_orders checks for already existing orders and try keeps them up to date.
There are also queues low and normal, for calculating users' orders and pulling their balances. 

You can run celery in several terminal windows or screen sessions:
```sh
celery worker -A djangoTrade -n worker_high -l info -c 1 -Q high
celery worker -A djangoTrade -n worker_set_orders -l info -c 1 -Q set_orders
celery worker -A djangoTrade -n worker_low -l info -c 2 -Q low
celery worker -A djangoTrade -n worker_normal -l info -c 2 -Q normal
```

Example of running celery with supervisor daemon:

```sh
wget https://raw.githubusercontent.com/celery/celery/4.0/extra/generic-init.d/celeryd -O /etc/init.d/celeryd
wget https://raw.githubusercontent.com/celery/celery/4.0/extra/generic-init.d/celerybeat -O /etc/init.d/celerybeat
chmod +x /etc/init.d/celeryd /etc/init.d/celerybeat

#add celery config
read -d "" CELERYD_CFG <<"EOF"
CELERYD_NODES="worker_set_orders worker_low worker_normal worker_high"
CELERY_BIN="/opt/env/bin/python -m celery"
CELERY_APP="djangoTrade"
CELERYD_CHDIR="/opt/ongrid_portal"
CELERYD_OPTS="-Q:worker_set_orders set_orders -Q:worker_low low -Q:worker_normal normal -Q:worker_high high -c:worker_set_orders 1 -c:worker_low 3 -c:worker_normal 3 -c:worker_high 1"
CELERYD_LOG_FILE="/var/log/celery/%n%I.log"
CELERYD_PID_FILE="/var/run/celery/%n.pid"
CELERYD_USER="root"
CELERYD_GROUP="root"
DJANGO_SETTINGS_MODULE="djangoTrade.settings"
CELERY_CREATE_DIRS=1
SECRET_KEY="ada#qadaa2d#1232%!^&#*(&@(!&Y!&#*T!@(^F#!@&#F!@&#F!(@"
EOF
echo "$CELERYD_CFG" > /etc/default/celeryd

read -d "" CELERYBEAT_CFG <<"EOF"
CELERY_BIN="/opt/env/bin/python -m celery"
CELERY_APP="djangoTrade"
CELERYD_CHDIR="/opt/ongrid_portal"
DJANGO_SETTINGS_MODULE="djangoTrade.settings"
CELERYBEAT_USER="root"
CELERYBEAT_GROUP="root"
EOF
echo "$CELERYBEAT_CFG" > /etc/default/celerybeat

/etc/init.d/celeryd create-paths
/etc/init.d/celeryd start
/etc/init.d/celeryd stop
/etc/init.d/celerybeat create-paths
/etc/init.d/celerybeat start
/etc/init.d/celerybeat stop
sudo update-rc.d celeryd defaults
sudo update-rc.d celerybeat defaults
```

## Authors
* OnGrid Systems: [Site](https://ongrid.pro), [GitHub](https://github.com/OnGridSystems/), [FaceBook](https://www.facebook.com/ongrid.pro/), [Youtube](https://www.youtube.com/channel/UCT8s-f1FInO6ivn_dp-W34g), [LinkedIn](https://www.linkedin.com/company/ongridpro/)
* Sergey Korotko [FaceBook](https://www.facebook.com/s.korotko), [GitHub](https://github.com/achievement008)
* Dmitry Suldin [FaceBook](https://www.facebook.com/novator.klin), [GitHub](https://github.com/Klyaus)
* Kirill Varlamov: [GitHub](https://github.com/ongrid/), [FaceBook](https://www.facebook.com/kirill.varlamov.12), [LinkedIn](https://www.linkedin.com/in/kvarlamo/)

## License

Copyright (c) 2018 OnGrid Systems
Each file included in this repository is licensed under the [MIT license](LICENSE).