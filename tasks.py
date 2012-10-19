import os
import signal
import logging
import subprocess
from pyvirtualdisplay import Display
from selenium import webdriver
import shodan
from celery import Celery
from celery import group
from celery import exceptions
from celery import signals
import selenium.webdriver.chrome.service as service

logger = logging.getLogger(__name__)

try:
    API_KEY = os.environ['SHODAN_API_KEY']
except KeyError:
    print ("Put your shodan API key in the environment with:\n"
           "export SHODAN_API_KEY=yourkeyhere")
    exit()

QUERY = 'port:80 amazon'
celery = Celery('tasks', broker='amqp://')


# set up the xvfb display
display = Display(visible=0, size=(600, 600))
display.start()

service = service.Service('chromedriver')
service.start()

# Set up the webdriver
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
options.add_argument('--disable-java')
options.add_argument('--incognito')
#options.add_argument('--kiosk')
# http://peter.sh/experiments/chromium-command-line-switches/


@celery.task
def get_shodan_results(page=1):
    logger.info("getting results: %s", page)
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
    #print "get screenshot: %s" % result	
    ip = result['ip']
    try:
        driver = webdriver.Remote(service.service_url,
                              desired_capabilities=options.to_capabilities())

        driver.get('http://%s' % ip)
        logger.info('Loaded %s: %s' % (ip, driver.title))
        # this seems to require an absolute path for some reason
        driver.get_screenshot_as_file(os.path.join(os.getcwd(),
                                                   'out/%s.png' % ip))
    except exceptions.SoftTimeLimitExceeded:
        logger.info('Terminating overtime process')


@signals.worker_shutdown.connect
def worker_shutdown(sender=None, conf=None, **kwargs):
    logger.info('Shutting down worker...')
    driver.quit()
    service.stop()

if __name__ == '__main__':
    get_shodan_results.delay()
