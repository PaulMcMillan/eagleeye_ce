from time import sleep
import foreman
import logging

logger = logging.getLogger('foreman')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

from celery import Celery
inspect = Celery().control.inspect()

#res = foreman.get_shodan_results.delay()
res = foreman.get_screenshot({'ip': '54.245.108.85'})
while True:
    print res.status
    sleep(1)
    active = len(inspect.active().values()[0])
    if active == 0:
        exit()
