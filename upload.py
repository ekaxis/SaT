import subprocess
import logging
import time
from os.path import join, dirname
from apscheduler.schedulers.blocking import BlockingScheduler

PATH_BASH = '/bin/bash'
headers = {
    'hostname': HOSTNAME,
    'api-key': APIKEY
}

@sched.scheduled_job('cron', day_of_week='mon-fri', hour=10)
def sendfile(url, path_log, apikey, hostname):
    DIR = dirname(path_log)
    try:
        logfile = [('log', open(path_log, 'rb'))]
        response = requests.request('POST', url, headers=headers, files=logfile)
        msg = json.loads(response.text.encode('utf8', errors='replace'))
    except Exception as err:
        logging.error(' sendfile error: %s' % err)
    
    if response is None:
        logging.warning(' unable to send file')
        exit(0)

    if response.status_code == 200:
        status_code, text_response = subprocess.getstatusoutput(
            f'{PATH_BASH} tar -cvf {DIR}/fast-alert-$(date +%d-%m-%Y).tar.gz {path_log}')

        while True:
            try:
                os.remove(path_log)
                break
            except Exception as err:
                logging.critical(' could not delete log file, more details: %s' % err)
                time.sleep(2)

if __name__ == '__main__':
    sendfile()
