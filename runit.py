from time import sleep
import tasks
import logging

logger = logging.getLogger('foreman')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

from celery import Celery
inspect = Celery().control.inspect()

#res = tasks.get_shodan_results.delay()
res = foreman.get_screenshot.delay({'ip': 'google.com'})
while True:
    print res.status
    sleep(1)
    active = len(inspect.active().values()[0])
    if active == 0:
        exit()
