#!/usr/env/python3
import time
import logging
import os
import requests
import json
from config import *
from bot import Telebot
from alert import Alert
from daemon import Daemon


def error_and_exit(msg):
    logging.error(msg)
    print(msg)
    sys.exit(1)

class SaT(Daemon):

    def __init__(self, pidfile, ip, path_file, token, chat_id,
            stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        super().__init__(pidfile=pidfile)
        self.path_file = path_file
        self.bot = Telebot(chat_id, token)
        self.host = ip
        self.turn = 0

    """
    you should override this method when you subclass daemon. it will be called after the process has been
    daemonized by start() or restart().
    """
    def run(self):
        if not os.path.isfile(self.path_file):
            logging.error(' - path file log not found!'); self.stop()

        while True:
            try:
                self.running();
            except Exception as err:
                logging.warning(' - error to open logfile -> %s' % err)
            time.sleep(10)

    """função lê todo arquivo na espera de novas entradas, caso não haja ele aguarda
    25s no máximo (calculo feito pela quantidade de loops e tempo de espera) e fecha o arquivo
    retornando o controle a função que a chamou
    """
    def reading(self)-> bool:
        if not os.path.isfile(self.path_file): logging.error(' - error to open file log'); return False

        with open(self.path_file) as file:
            while True:
                line = file.readline().strip()
                if line: yield line
                else: # se não houver novas entradas
                    if self.turn <= 5:
                        time.sleep(10); self.turn+=1
                    else: return True   # retorna um boolean para liberar recursos

    def running(self)-> None:
        for number_line, line in enumerate(self.reading()):
            try:
                self.turn = 0
                alert = Alert.create_alert(self.host, line)
                if AlertModel.add(alert.alert()):
                    # condição para envio de mensagem no Telegram
                    if int(alert.alert_priority) <= 1:
                        num_alerts = len(AlertModel.select().where(AlertModel.msg == alert.msg))
                        self.bot.sendMessage(alert.telegram_alert(self.host, num_alerts))
            except Exception as err:
                logging.error(' error in running function: %s' % err)

    def status(self):
        try:
            with open(self.pidfile, 'r') as pf: pid = int(pf.read().strip())
        except IOError: pid = None
    
        if pid:
            print(' - running')
        else:
            print(' - inactive')


if __name__ == "__main__":
    if not os.path.isfile(PATH_ALERTS):
        error_and_exit('path file alerts not found')

    sat = SaT(pidfile=PATH_PIDFILE, ip=IP, path_file=PATH_ALERTS, token=TOKEN, chat_id=CHAT_ID)
    
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            logging.info('starting [SaT tool]')
            sat.start()
        elif 'stop' == sys.argv[1]:
            logging.info('stopping [SaT tool]')
            sat.stop()
        elif 'restart' == sys.argv[1]:
            logging.info('restarting [SaT tool]')
            sat.restart()
        elif 'status' == sys.argv[1]:
            sat.status()
        else:
            print("unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        print(" usage: %s start|stop|restart|status" % sys.argv[0])
        sys.exit(2)
