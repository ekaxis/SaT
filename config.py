import os, logging, sys
from os.path import join, dirname
from dotenv import load_dotenv
from model import AlertModel
from upload import sendfile
import peewee, telepot
from apscheduler.schedulers.blocking import BlockingScheduler

# import os >>> os.makedirs ('/ hey / oi / ola') 
#
# dependências do python - pip
# dotenv-python==0.0.1
# peewee==3.13.3
# telepot==12.7
# requests==2.23.0
# 
# versão feita e testada - Python 3.8.2 (x86-64)
# pip install -r requirements.txt
#
# configurações logging (DEBUG) 
logging.getLogger('peewee').setLevel(logging.WARNING) # disable debug insert 
logging.getLogger('telepot').setLevel(logging.WARNING)
#
dotenv_path = join(dirname(__file__), 'SaT.conf')
if not os.path.isfile(dotenv_path):
    print(' - [!] configure file SaT.conf'); sys.exit(0)
# carregar variáveis de ambiente
load_dotenv(dotenv_path=dotenv_path)
# config logging
PATH_LOG = os.environ.get('PATH_LOG')
format_logging = '%(asctime)s %(levelname)s\t %(message)s' # 17/05/2020 17:05:05 INFO     * Restarting with stat
datefmt = '%d/%m/%Y %H:%I:%M'  # 27/04/2020 20:49
filename_log = PATH_LOG # absolute path
logging.basicConfig(level=logging.DEBUG, filename=filename_log, format=format_logging, filemode='a+', datefmt=datefmt)
# nids configurações
PATH_ALERTS = os.environ.get('PATH_ALERTS')
IP = os.environ.get('IP')
# WARN config server
SEND_FILE = os.environ.get('SEND_FILE')
URL = os.environ.get('URL')
HOSTNAME = os.environ.get('HOSTNAME')
APIKEY = os.environ.get('APIKEY')
# banco de dados SQLite
try:
    AlertModel.create_table()
except Exception as e:
    logging.error(' [err] %s' % e); sys.exit(0)
# telegram config infos
TOKEN = os.environ.get('TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
# pidfile path
PATH_PIDFILE = os.environ.get('PATH_PIDFILE')
# agendar envio do arquivo do log
if SEND_FILE:
    scheduler = BlockingScheduler()
    sched.start()