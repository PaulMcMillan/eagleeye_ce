import os
import signal
import logging
import subprocess

import requests
import shodan
from celery import Celery, group, exceptions

logger = logging.getLogger(__name__)


API_KEY = os.environ['SHODAN_API_KEY']
QUERY = 'port:80 amazon'
celery = Celery('tasks', backend='redis://localhost', broker='amqp://')


@celery.task
def get_shodan_results(page=1):
    print "getting results: %s" % page
    api = shodan.WebAPI(API_KEY)
    try:
        res = api.search(QUERY, page=page)
    except shodan.api.WebAPIError:
        logger.info('Finished shodan results with %s page(s).', page -1)
    else:
        print group(get_screenshot.s(x) for x in res['matches']).apply_async()
        get_shodan_results.delay(page=page+1)
        return res


@celery.task
def get_screenshot(result):
    print "get screenshot: %s" % result	
    ip = result['ip']
    try:
        res = requests.head('http://%s/' % ip, timeout=2)
    except requests.exceptions.Timeout:
        return
    except requests.exceptions.ConnectionError:
        logger.info('Connection Error to %s', ip)
        return
    try:
        def subprocess_setup():
            # Python installs a SIGPIPE handler by default. This is
            # usually not what non-Python subprocesses expect.
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

        cmd = ['./wkhtmltoimage-amd64',
               '--width', '600',
               '--load-error-handling', 'ignore',
               'http://%s/' % ip,
               'out/%s.png' % ip]
        os.setpgrp()
        p = subprocess.Popen(cmd, preexec_fn=subprocess_setup,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
    except exceptions.SoftTimeLimitExceeded:
        logger.info('Terminating overtime process')
        p.stdout.close()
        sleep(1)
        p.terminate()
        sleep(1)
        p.kill()
        os.killpg(p.pid, signal.SIGKILL)
        p.wait()
        print "got to the end of a wait"
