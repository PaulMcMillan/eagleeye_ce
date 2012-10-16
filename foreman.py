import os
import logging
import subprocess

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
        p = subprocess.Popen(['./wkhtmltoimage-amd64', '--width', '600', '--load-error-handling', 'ignore', 'http://%s/' % ip, 'out/%s.png' % ip])
    except exceptions.SoftTimeLimitExceeded:
        logger.info('Terminating overtime process')
        p.terminate()



