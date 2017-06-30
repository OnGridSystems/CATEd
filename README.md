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
    
