# OnGrid portal

# Installation
Start from clean Ubuntu 16 LTS installation

If your system has no swap partition you should make swap file to avoid low memory conditions

```sh
dd if=/dev/zero of=/swapfile bs=1M count=2000
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo "/swapfile   none    swap    sw    0   0" >> /etc/fstab
```

Upgrade packages and grub

```
echo -e "LC_ALL=en_US.UTF-8\nLANG=en_US.UTF-8" >> /etc/environment
read -d "" UPGRADESCRIPT <<"EOF"
export DEBIAN_FRONTEND=noninteractive
apt purge -y grub-pc grub-common
apt autoremove -y 
rm -rf /etc/grub.d/
apt -y update
apt upgrade -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" 
apt install -y git mysql-server libmysqlclient-dev libssl-dev openssl rabbitmq-server screen vim gcc make python3-pip python3-venv
apt install -y grub-pc grub-common
grub-install /dev/vda
update-grub
EOF
echo "$UPGRADESCRIPT" > /tmp/upgradescript
bash /tmp/upgradescript
```

and

```sh
reboot
```

After server bringup make SSH keys and settings

```sh
mkdir /root/.ssh
chmod 0755 /root/.ssh
touch /root/.ssh/id_rsa.pub
chmod 0644 /root/.ssh/id_rsa.pub
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDjRBWiF26Eb1pVsMl7Nxv2bplH+sHqbeSkDYuaWpryWNAs+070/qzoI4oo+8jybFf7yinhGb8msD0xU5a7c17aDnMI9f1AIKZIuBUaNp1rgH1R6ATJTXSQGK3YPl/Jncc9MNBoCyiKlpn/DVhmcTslECGGlFVfIHQT2rQh3qFNxhVK5R5SUBdxaxQ+pYKnABl0kzwb6bV+S7kHNPA8N5t95EFOsFQZ3JBTHZsqY2GPS8UBcKtmbixb/YcYm50CiypuiivnOec0CfbLPhssMhcAzpQuI3tKgdVa3It7/MVUlpXCC9q9xRyWvSd/ycKIBW0YZv1ZwWLB+3RlI0NnDtr1 root@portal" > /root/.ssh/id_rsa.pub
touch /root/.ssh/id_rsa
chmod 0600 /root/.ssh/id_rsa
read -d "" RSAID <<"EOF"
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA40QVohduhG9aVbDJezcb9m6ZR/rB6m3kpA2Lmlqa8ljQLPtO
9P6s6COKKPvI8mxX+8op4Rm/JrA9MVOWu3Ne2g5zCPX9QCCmSLgVGjada4B9UegE
yU10kBit2D5fyZ3HPTDQaAsoipaZ/w1YZnE7JRAhhpRVXyB0E9q0Id6hTcYVSuUe
UlAXcWsUPqWCpwAZdJM8G+m1fku5BzTwPDebfeRBTrBUGdyQUx2bKmNhj0vFAXCr
Zm4sW/2HGJudAosqboor5znnNAn2yz4bLDIXAM6ULiN7SoHVWtyLe/zFVJaVwgva
vcUclr0nf8nCiAVtGGb9WcFiwft0ZSNDZw7a9QIDAQABAoIBADSj9I7S9ppeYIIw
rLqJjUSLYZ22i2wNgEQvjwJ1siYoRC/nFebRhqNOeBX+HBFq3wZHUWP+XrRLZiEi
x2sr0fCYIDUXJU3RQjLd0KV9uQDJhj2OjG1EL5eg38OSzwUYMqoNwHgY/Y78Szc0
lCFGYPi4v8s4WH3sOnbO1aJyutIUe9e0XozucWktVOyA8K1LcjBkwuHefOFxFUug
ooytB/zJJ4SqmBfvUJag+og5ZSStwu86SuacVbd/VAl4ecn2l+8cvQ9dwlkEWadN
N6QchnmBqn310EX1JSNX6aT579YP8s7abl+eJEVApOvj+W/9BYHIY+rR9QTQCOs1
Dp+E5RECgYEA+JFo1Yl3rjOcI55Jy1VMO6UzWnCFD9Q/CftLi6x/7WlRd81ZsjIc
ne8L14eBjXA5LnQoGwneUgxgI+QVuwiN/kgozoqDZ/DCaZlt4u5ouN55Q5NcX+G0
fH19w+9V3xeviKM2y9633D6IFz1+xFHiROU4q7JpZnXCi2jRtJojaE8CgYEA6g+f
7l637LjN00BnGLCLmmxMMjyJs8OVK8NLkuHjLb8Et5kuwJ+DXIkk+EzO2Z4uL0Id
jst5c5OYEPYdzwwg5IyRDdQQhgd3iThxdc6uiylHazBkg7O5IA67Ld3x5eaPnLCE
1LBLlWsUce2NNqx7s/3KUZl7vZVT/6n8zPx8M3sCgYBLnei3dU9cRkUMrN2kJrm/
N11s+Ofxzc6zmaf8wKhWMADhoi3UQNxly0/d7FIkFey/TgTZXOIuMaeZo4xczphr
r8YCNy8MkriB6XP9Yiuneb6IKS8j2ATRDlgRICEOciUrOwOzd3iVXsyFzWZgEMz1
yom36dmYmuBpCqUo/O8ijwKBgQCjiTM3O1rKvPyiY1clOwTvakd6ui2EOl0ZbKR7
BfTS26oSFadC0rDXkMMR8ah9CDZAsrMwOB6tkCwpfayqI1FAHq6iuM6qtsDgUV2E
8FmnxbmuvOsd0g7AxUom6/G9rfAdjH/ikyLcTSrFxzJpRu5Pfj1D8jcw6Qr9kOme
17J3zQKBgEtmtRZCru4F6lIqRHQ0LuKSWmQj5GMWpUQpAknU0FsYVuOARy2zG82r
Q96LKk79rktYZLJfSbBQFs2T0OOO55VHQ/SIm8zhYvCiCG/FGWZedtC1Je/HhZad
qrML3yarOYprFN8CupDTwbgIETx+DA5k1eUELraMiJcdx9Pme3H4
-----END RSA PRIVATE KEY-----
EOF
#
# Change SSH configuration to disable github key prompt
echo "$RSAID" > /root/.ssh/id_rsa
read -d "" SSHCFG <<"EOF"
Host github.com
    StrictHostKeyChecking no 
    UserKnownHostsFile /dev/null
    LogLevel QUIET
EOF
echo "$SSHCFG" >> /etc/ssh/ssh_config

```

Install python virtualenv, create configs, clone project from git and apply some patches

```sh
pip3 install --upgrade pip setuptools wheel
cd /opt
mkdir portal_ongrid
cd portal_ongrid
mkdir logs static media configs
python3 -m venv env
cd /opt/portal_ongrid/configs
touch supervisor.conf
touch nginx.conf
touch djangoTrade

#
#set config for gunicorn
read -d "" DJTRD<<"EOF"
#!/bin/sh

NAME="djangoTrade"                                  
DJANGODIR=/opt/portal_ongrid/ongrid_portal/             
USER=root                                        
GROUP=root                                     
NUM_WORKERS=2                                    
DJANGO_SETTINGS_MODULE=djangoTrade.settings            
DJANGO_WSGI_MODULE=djangoTrade.wsgi                     
echo "Starting $NAME as `whoami`"
cd $DJANGODIR
source ../env/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR
exec ../env/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER --group=$GROUP \
  --bind="127.0.0.1:9023" \
  --log-level=debug \
  --log-file=-
EOF
echo "$DJTRD" > /opt/portal_ongrid/configs/djangoTrade
chmod u+x /opt/portal_ongrid/configs/djangoTrade

#
#set config for nginx
read -d "" NGINX <<"EOF"
server {
    listen 80;
    server_name 127.0.0.1 portal.ongrid.pro www.portal.ongrid.pro;
    access_log  /opt/portal_ongrid/logs/nginx_access.log;
    client_max_body_size 100M;

    location /media  {
        alias /opt/portal_ongrid/media;
        expires 30d;
        add_header Pragma public;
        add_header Cache-Control "public";
    }
    location /static {
        alias /opt/portal_ongrid/static;
        expires 30d;
        add_header Pragma public;
        add_header Cache-Control "public";
    }

    location / {
        proxy_pass http://127.0.0.1:9023;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_connect_timeout       600;
        proxy_send_timeout          600;
        proxy_read_timeout          600;
        send_timeout                600;
    }

  }
EOF
echo "$NGINX" > /opt/portal_ongrid/configs/nginx.conf

#
#set config for supervisor
read -d "" VISOR <<"EOF"
[program:djangoTrade_web]
command = /opt/portal_ongrid/configs/djangoTrade
user = root
stdout_logfile = /opt/portal_ongrid/logs/gunicorn_supervisor.log
redirect_stderr = true
environment=LANG=en_US.UTF-8,LC_ALL=en_US.UTF-8
EOF
echo "$VISOR" > /opt/portal_ongrid/configs/supervisor.conf

cd /opt/portal_ongrid
source /opt/portal_ongrid/env/bin/activate
pip install --upgrade pip setuptools wheel
git clone git@github.com:ongrid/ongrid_portal.git
cd ongrid_portal
pip install gunicorn==19.6.0
pip install -r requirements.txt

#
#patching configuration
read -d "" PATCH <<"EOF"
50c50
< DEBUG = True
---
> DEBUG = False
52c52
< ALLOWED_HOSTS = ['127.0.0.1']
---
> ALLOWED_HOSTS = ['portal.ongrid.pro', 'www.portal.ongrid.pro']
127c127
<         'NAME': 'tradenew',
---
>         'NAME': 'trade',
129c129
<         'PASSWORD': '123',
---
>         'PASSWORD': '',
170c170
< YANDEX_MONEY_CLIENT_ID = 'BDDFD147E2F62EA4827F2F28E652CEF2F5AD328D0C1575E4F0AD8E56FCADD5CF'
---
> YANDEX_MONEY_CLIENT_ID = '1EB2214C53CF879A9BD8606934B804F93BE9C82604DD9A1ED967F8635CBCD04B'
172c172
< YANDEX_MONEY_REDIRECT_URI = 'http://78.155.218.16:8000/wallet/'
---
> YANDEX_MONEY_REDIRECT_URI = 'http://portal.ongrid.pro/wallet/'
174c174
< YANDEX_MONEY_CLIENT_SECRET = '211A8533870D422A3EAB307B20897DB1A76EFD1379263CFD69FEC67630EA304A4831D7813BDEC90A866ABED2C30B9F8578EFF29962B13B70187429034EA3BF59'
---
> YANDEX_MONEY_CLIENT_SECRET = 'DD89A956C22739F77FDA276D64E9DF2E711DAA7645BFA5741872C0DA93DA8240EDDB6FBD2500210891396231AF4FB5B2FD90C7C0BB45F51803EAA36105CE508F'
EOF
echo "$PATCH" | patch djangoTrade/settings.py

#
# patching poloniex library
read -d "" PATCH <<"EOF"
128c128
<             signature = _hmac.new(self._secret, request.body, _hashlib.sha512)
---
>             signature = _hmac.new(self._secret, request.body.encode(), _hashlib.sha512)
EOF
echo "$PATCH" | patch /opt/env/lib/python3.5/site-packages/poloniex/poloniex.py

```

set databases and mocks

```sh
echo "create database trade character set utf8" | mysql -u root
mysql -u root trade < dump.sql
#
# Migrate
/opt/env/bin/python3 manage.py makemigrations
/opt/env/bin/python3 manage.py migrate
#
# Add users
read -d "" PYCODE <<"EOF"
from django.contrib.auth.models import User
user = User.objects.create_user(username='kirill',
                                 email='kirill@ongrid.pro',
                                 password='kirill')
EOF
echo "$PYCODE" | /opt/env/bin/python3 manage.py shell
```

install and configure celery

```sh
wget https://raw.githubusercontent.com/celery/celery/4.0/extra/generic-init.d/celeryd -O /etc/init.d/celeryd
wget https://raw.githubusercontent.com/celery/celery/4.0/extra/generic-init.d/celerybeat -O /etc/init.d/celerybeat
chmod +x /etc/init.d/celeryd /etc/init.d/celerybeat
read -d "" CELERYD_CFG <<"EOF"
CELERY_BIN="/opt/portal_ongrid/env/bin/python -m celery"
CELERY_APP="djangoTrade"
CELERYD_CHDIR="/opt/portal_ongrid/ongrid_portal"
CELERYD_OPTS="--time-limit=300 --concurrency=1"
CELERYD_LOG_FILE="/var/log/celery/%n%I.log"
CELERYD_PID_FILE="/var/run/celery/%n.pid"
CELERYD_USER="root"
CELERYD_GROUP="root"
DJANGO_SETTINGS_MODULE="djangoTrade.settings"
CELERY_CREATE_DIRS=1
SECRET_KEY="ada#qadaa2d#1232%!^&#*(&@(!&Y!&#*T!@(^F#!@&#F!@&#F!(@"
EOF
echo "$CELERYD_CFG" > /etc/default/celeryd
/etc/init.d/celeryd create-paths
/etc/init.d/celeryd start
/etc/init.d/celeryd stop
sudo update-rc.d celeryd defaults
```

make all components start on boot in screens

```sh
read -d "" RCLOCAL <<"EOF"
#!/bin/bash
cd /opt/portal_ongrid
source ./env/bin/activate
screen -dmS ongrid_portal bash -c 'cd ongrid_portal; celery beat -A djangoTrade -l=INFO'
exit 0
EOF
echo "$RCLOCAL" > /etc/rc.local
#
```

reboot and have fun!

# Old installation manual

Развернуть проект на встроенном сервере Django:
  1) Заходим на сервер, в папку где будет лежать проект.
  2) mkdir projectname
  Если надо виртуальное пространствj:
    3) sudo apt-get install python3-venv
    4) python3 -m venv env
    5) . env/bin/activate
  6) git clone https://github.com/ongrid/ongrid_portal.git
  7) cd ongrid_portal
  8) pip install -r requirements.txt
  9) sudo apt-get rabbitmq-server
  Далее создаем базу данных, например MySQL:
  10) sudo apt-get install mysql-server
  11) mysql -u root
    12) create database trade character set utf8;
    13) exit;
  Производим необходимые настройки проекта:
    14) sudo nano djangoTrade/settings.py
      В блоке DATABASES необходимо указать имя пользователя и пароль от базы данных, и имя самой базы.
      Переменной ALLOWED_HOSTS присвоить значение: ['ip.адрес.сервера']
      CTRL+O -> Enter ->CTRL+X
    15) python manage.py migrate
    16) mysql -u root < dump.sql
    17) python manage.py createsuperuser
      имя пользователя
      email пользователя
      пароль 2 раза


Установка celery как демона
  1) sudo wget https://raw.githubusercontent.com/celery/celery/4.0/extra/generic-init.d/celeryd -O /etc/init.d/celeryd
  2) sudo wget https://raw.githubusercontent.com/celery/celery/4.0/extra/generic-init.d/celerybeat -O /etc/init.d/celerybeat
  3) sudo chmod +x /etc/init.d/celeryd
     sudo chmod +x /etc/init.d/celerybeat
  4) sudo nano /etc/default/celeryd

      CELERY_BIN="/home/projects/ongrid-portal/env/bin/python -m celery" #путь к celery в виртуальном окружении
      CELERY_APP="djangoTrade" #Название приложения
      CELERYD_CHDIR="/home/projects/ongrid-portal/ongrid_portal" #Папка с проектом
      CELERYD_OPTS="--time-limit=300 --concurrency=1" #Параметры запуска celery (--concurrency устанавливает количество воркеров)
      CELERYD_LOG_FILE="/var/log/celery/%n%I.log" #Путь для логов воркеров
      CELERYD_PID_FILE="/var/run/celery/%n.pid" #--
      CELERYD_USER="root" #от кого запускать celery
      CELERYD_GROUP="root" #--
      export DJANGO_SETTINGS_MODULE="djangoTrade.settings" #Модуль настроек django
      CELERY_CREATE_DIRS=1
      export SECRET_KEY="ada#qadaa2d#1232%!^&#*(&@(!&Y!&#*T!@(^F#!@&#F!@&#F!(@"
   5) reboot now
   6) sudo /etc/init.d/celeryd start
   7) cd /path/to/project/
   8) . env/bin/activate
   9) cd ongrid_portal
   10) celery beat -A djangoTrade -l=INFO
   
   
Проверка отдельных заданий для celery:
В папке с проектом:
  1) python manage.py shell
  2) from trade import tasks
  3) var = tasks.start_trade_btce
                 start_trade_poloniex
                 start_trade_bittrex
                 get_eth_wallet_history
                 get_btc_wallet_history
                 get_yandex_wallet_history
                 calculate_holdings_history.delay() - отправит задание в очередь заданий
  Желательно в отдельном окне, в папке с проектом и активированным виртуальным окружением
  celery worker -A djangoTrade -l=INFO
  worker должен получить отправленое задание и начать его выполнять.
  
  
  Запуск сервера:
    В папке с проектом и активированным виртуальным окружением:
    python manage.py runserver 0.0.0.0:8000 - запустит сервер по адресу сервера на 8000 порте.
    
