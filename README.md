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
apt install -y git mysql-server libmysqlclient-dev libssl-dev openssl rabbitmq-server screen vim gcc make python3-pip python3-venv htop mc nginx smem supervisor libjpeg-dev libfreetype6-dev zlib1g-dev libxml2-dev libxslt1-dev links
service supervisor restart  
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
  server_name  portal.ongrid.pro www.portal.ongrid.pro;
  rewrite  ^(.*) https://$server_name$1 permanent;
}
server {
    listen 443 ssl;
    server_name 127.0.0.1 portal.ongrid.pro www.portal.ongrid.pro;
    access_log  /opt/portal_ongrid/logs/nginx_access.log;
    client_max_body_size 100M;
    keepalive_timeout    60;
    ssl_certificate      /etc/letsencrypt/ongrid.crt;
    ssl_certificate_key  /etc/letsencrypt/private.key;
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
    ssl_ciphers  "HIGH:!RC4:!aNULL:!MD5:!kEDH";
    add_header Strict-Transport-Security 'max-age=604800';
   
    location /.well-known {
        alias /.well-known;
    }
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
echo "$PATCH" | patch /opt/portal_ongrid/env/lib/python3.5/site-packages/poloniex/poloniex.py

```

set databases and mocks

```sh
echo "create database trade character set utf8" | mysql -u root
mysql -u root trade < dump.sql
#
# Migrate
./manage.py makemigrations
./manage.py makemigrations tradeBOT
./manage.py migrate
#
# Add users
read -d "" PYCODE <<"EOF"
from django.contrib.auth.models import User
user = User.objects.create_user(username='kirill',
                                 email='kirill@ongrid.pro',
                                 password='kirill')
EOF
echo "$PYCODE" | ./manage.py shell
ln -s /opt/portal_ongrid/configs/supervisor.conf /etc/supervisor/conf.d/djangoTrade.conf
ln -s /opt/portal_ongrid/configs/nginx.conf /etc/nginx/sites-enabled/portal_ongrid.conf
supervisorctl update
supervisorctl restart djangoTrade_web
./manage.py collectstatic --noinput
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

Set SSL certificate (12.10.2017, 13:00:00)
```sh
cd /etc
mkdir letsencrypt
cd letsencrypt
touch ongrid.crt
touch private.key
read -d "" CERT<<"EOF"
-----BEGIN CERTIFICATE-----
MIIFBTCCA+2gAwIBAgISA3/inLnXFdE7eV6iZy15zN83MA0GCSqGSIb3DQEBCwUA
MEoxCzAJBgNVBAYTAlVTMRYwFAYDVQQKEw1MZXQncyBFbmNyeXB0MSMwIQYDVQQD
ExpMZXQncyBFbmNyeXB0IEF1dGhvcml0eSBYMzAeFw0xNzA3MTQxMDAwMDBaFw0x
NzEwMTIxMDAwMDBaMBwxGjAYBgNVBAMTEXBvcnRhbC5vbmdyaWQucHJvMIIBIjAN
BgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvft5fOL9fwj91Sx+VePqQuNPUMYE
O04+y0lz5QpPI6EWseDQrRzBbG50L+CenBd9w96jgSaQW+6D7Dj6sGJAMJwbT/5u
sai+ZFStgFsEkAKVBx3RnxUo8ihFllndG8uKu8M3q3iRZk6a4nz+TznENVAkwRpf
V6FZNVuth2QTFNmGdTNbli7672YIcactnQxGdSra6t6OFZhk1i+olugKTEKgaD0l
VXy5uDfMTstd5DcEVqkOvaeJaxkDXnhDmRIV4v9rYeveOCB+35wGOvuY4S7Xy6VV
uQagwhn0jfaJ90L0Jtj8/9USWqTqVq9upja+g3AjfS7jkQSVoWH5s2dyRQIDAQAB
o4ICETCCAg0wDgYDVR0PAQH/BAQDAgWgMB0GA1UdJQQWMBQGCCsGAQUFBwMBBggr
BgEFBQcDAjAMBgNVHRMBAf8EAjAAMB0GA1UdDgQWBBQufjoegphavRu105iUzhBe
F3ENWjAfBgNVHSMEGDAWgBSoSmpjBH3duubRObemRWXv86jsoTBvBggrBgEFBQcB
AQRjMGEwLgYIKwYBBQUHMAGGImh0dHA6Ly9vY3NwLmludC14My5sZXRzZW5jcnlw
dC5vcmcwLwYIKwYBBQUHMAKGI2h0dHA6Ly9jZXJ0LmludC14My5sZXRzZW5jcnlw
dC5vcmcvMBwGA1UdEQQVMBOCEXBvcnRhbC5vbmdyaWQucHJvMIH+BgNVHSAEgfYw
gfMwCAYGZ4EMAQIBMIHmBgsrBgEEAYLfEwEBATCB1jAmBggrBgEFBQcCARYaaHR0
cDovL2Nwcy5sZXRzZW5jcnlwdC5vcmcwgasGCCsGAQUFBwICMIGeDIGbVGhpcyBD
ZXJ0aWZpY2F0ZSBtYXkgb25seSBiZSByZWxpZWQgdXBvbiBieSBSZWx5aW5nIFBh
cnRpZXMgYW5kIG9ubHkgaW4gYWNjb3JkYW5jZSB3aXRoIHRoZSBDZXJ0aWZpY2F0
ZSBQb2xpY3kgZm91bmQgYXQgaHR0cHM6Ly9sZXRzZW5jcnlwdC5vcmcvcmVwb3Np
dG9yeS8wDQYJKoZIhvcNAQELBQADggEBAH1yiifbBsnv9KV9Pxmdo8+ZR2UgqCHp
Z4FrcENBWleHpDopPvd0h7Jsxa6IkjvM4JA0ITrC9ZMckQUPfcmBzC/13efPjtl6
VcGBGQmfiNWvoAvpKF7cYOHGZ6LQfQ5M3wKfTC27si/vwaeL0277yO1EpcG/ZJYx
LCYnE0TFN5+EFIGpneAolGu30Rxpe86IFcEH+KhW2k6vwrlbpN/XF9ENvTTu740T
WsGSo6XtYfhr2gPQi/glC605TnN3Jv/fSXKxvKj6hMMb3FpANqZBPuAKfrsXudxY
yGN6qyNB2XeJV1IeHD9HeFTmaRx++SYybGDIwUKbFDWuHF1iN2PGZu4=
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIEkjCCA3qgAwIBAgIQCgFBQgAAAVOFc2oLheynCDANBgkqhkiG9w0BAQsFADA/
MSQwIgYDVQQKExtEaWdpdGFsIFNpZ25hdHVyZSBUcnVzdCBDby4xFzAVBgNVBAMT
DkRTVCBSb290IENBIFgzMB4XDTE2MDMxNzE2NDA0NloXDTIxMDMxNzE2NDA0Nlow
SjELMAkGA1UEBhMCVVMxFjAUBgNVBAoTDUxldCdzIEVuY3J5cHQxIzAhBgNVBAMT
GkxldCdzIEVuY3J5cHQgQXV0aG9yaXR5IFgzMIIBIjANBgkqhkiG9w0BAQEFAAOC
AQ8AMIIBCgKCAQEAnNMM8FrlLke3cl03g7NoYzDq1zUmGSXhvb418XCSL7e4S0EF
q6meNQhY7LEqxGiHC6PjdeTm86dicbp5gWAf15Gan/PQeGdxyGkOlZHP/uaZ6WA8
SMx+yk13EiSdRxta67nsHjcAHJyse6cF6s5K671B5TaYucv9bTyWaN8jKkKQDIZ0
Z8h/pZq4UmEUEz9l6YKHy9v6Dlb2honzhT+Xhq+w3Brvaw2VFn3EK6BlspkENnWA
a6xK8xuQSXgvopZPKiAlKQTGdMDQMc2PMTiVFrqoM7hD8bEfwzB/onkxEz0tNvjj
/PIzark5McWvxI0NHWQWM6r6hCm21AvA2H3DkwIDAQABo4IBfTCCAXkwEgYDVR0T
AQH/BAgwBgEB/wIBADAOBgNVHQ8BAf8EBAMCAYYwfwYIKwYBBQUHAQEEczBxMDIG
CCsGAQUFBzABhiZodHRwOi8vaXNyZy50cnVzdGlkLm9jc3AuaWRlbnRydXN0LmNv
bTA7BggrBgEFBQcwAoYvaHR0cDovL2FwcHMuaWRlbnRydXN0LmNvbS9yb290cy9k
c3Ryb290Y2F4My5wN2MwHwYDVR0jBBgwFoAUxKexpHsscfrb4UuQdf/EFWCFiRAw
VAYDVR0gBE0wSzAIBgZngQwBAgEwPwYLKwYBBAGC3xMBAQEwMDAuBggrBgEFBQcC
ARYiaHR0cDovL2Nwcy5yb290LXgxLmxldHNlbmNyeXB0Lm9yZzA8BgNVHR8ENTAz
MDGgL6AthitodHRwOi8vY3JsLmlkZW50cnVzdC5jb20vRFNUUk9PVENBWDNDUkwu
Y3JsMB0GA1UdDgQWBBSoSmpjBH3duubRObemRWXv86jsoTANBgkqhkiG9w0BAQsF
AAOCAQEA3TPXEfNjWDjdGBX7CVW+dla5cEilaUcne8IkCJLxWh9KEik3JHRRHGJo
uM2VcGfl96S8TihRzZvoroed6ti6WqEBmtzw3Wodatg+VyOeph4EYpr/1wXKtx8/
wApIvJSwtmVi4MFU5aMqrSDE6ea73Mj2tcMyo5jMd6jmeWUHK8so/joWUoHOUgwu
X4Po1QYz+3dszkDqMp4fklxBwXRsW10KXzPMTZ+sOPAveyxindmjkW8lGy+QsRlG
PfZ+G6Z6h7mjem0Y+iWlkYcV4PIWL1iwBi8saCbGS5jN2p8M+X+Q7UNKEkROb3N6
KOqkqm57TH2H3eDJAkSnh6/DNFu0Qg==
-----END CERTIFICATE-----
EOF
echo "$CERT" > /etc/letsencrypt/ongrid.crt

read -d "" KEY<<"EOF"
-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC9+3l84v1/CP3V
LH5V4+pC409QxgQ7Tj7LSXPlCk8joRax4NCtHMFsbnQv4J6cF33D3qOBJpBb7oPs
OPqwYkAwnBtP/m6xqL5kVK2AWwSQApUHHdGfFSjyKEWWWd0by4q7wzereJFmTpri
fP5POcQ1UCTBGl9XoVk1W62HZBMU2YZ1M1uWLvrvZghxpy2dDEZ1Ktrq3o4VmGTW
L6iW6ApMQqBoPSVVfLm4N8xOy13kNwRWqQ69p4lrGQNeeEOZEhXi/2th6944IH7f
nAY6+5jhLtfLpVW5BqDCGfSN9on3QvQm2Pz/1RJapOpWr26mNr6DcCN9LuORBJWh
YfmzZ3JFAgMBAAECggEAD98JWDCSYuF6ayurZjuDH5Fj1+ijA91Wi58YSoMg92YG
wld4t22WjxtvI2zNc1bXD9zypeB14Og9JyffcYrTt/vioD0uPDNPrIwSbo2sBOfi
UVThZTvcTtakcZoSSbcoYOU/KlkJNJXOhKtSh4XY6WdHmsY8PtLg4/9DsPLgUTZy
Et8Tt4ozlPRXNRyb+7LbR3Rg1FWc6hfYSVh8eUYwZeoNlyN12CbAhZQ878DApHTi
CUu97UGqbOzeM/DpJzXDz7tDC5K3eMJetFPSwOBqmHQhTWdx9YuVVmA7gXmLKdJ4
4HQvGUaVo8PV1iDLnFq1TNFGUYjYIdjDD4cOwDlS4QKBgQDjRlDci0zHZ8O1ub/O
B4DiDH6pvKzGov08D8GlrnvmdN0XYEgoKSBYm2nqhaJwBHGmb08dqA6E7gpxS0sM
uOvoSA8wOOP2YlJJDcQlMQJe+0vjnmguZgNSEAn8RxoxEhO0vXEz4tyrIqMQ6PDV
pkRRi31aBA67cx4A8yCZJZyKbQKBgQDV/oeqK9oPSPtjt5XGt8diPlNuokYbcFOC
HugO459DBi4mdM6l8OdQB8Y8fygRrlK9bAOdtwZ+LAL3+DEjO0jHLpjB4LUYWQQN
wyL39uNqNH/ikhuQe8Kxf0Gt2g11xkto+6lceQ025sQxtaD3Hdtv18x8YM3I4p3U
ZfZFU9sgOQKBgQDFCACyMlGtzddthEs0Ymzpi8uDe36N9l9z4nUPHeVsNYQ279Ge
f4j7SEDagGACnNeqYnVEUJ3FwFhtP8kgjnB2P4JrW+bFgxezHaweUg6sKU/xVTMc
hnP6gM0nWLzsLa/H0TSCtvp3ot+bmVaw4iP4TeWuVDYxa+tnB2ALZQABQQKBgCuU
ycZTZfaE84WsZtlwpi+Q5+b5L3P5HVi7uKEHpHC++nkkgs1y0XkQDERX1S48pWck
b1wYYT8i8XvU1RUKxtih2cRqYhdSUawH2MBNTKVdicn33ZtASTdi5lpktScOOl9o
GWbW1GUg/EXvapfJQd52QZP3FxHZbTFLjqsx18epAoGAYSFs3ZLMfGI7CxdDeZUu
RHxfhHB8LCneUa3NaavfYAGB5OZMSHA88yKPh6/zQiVnAjv5FnzVFXExyIXdMh0y
hj7NDwUGVs3OAYZwa2GVPZJ9iiKq0wD+kdZV3Xk2BxAuU+NOvNrT3f2Z6KR0Xe5O
kyP/Ua+Xu2maz/FBXmJtd2I=
-----END PRIVATE KEY-----
EOF
echo "$KEY" > /etc/letsencrypt/private.key
```

reboot and have fun!