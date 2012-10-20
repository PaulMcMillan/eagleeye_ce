import os
import signal
import logging
import subprocess
from pyvirtualdisplay import Display
from selenium import webdriver
import selenium
import shodan
from celery import Celery
from celery import group
from celery import exceptions
from celery import Task
from celery import signals
import selenium.webdriver.chrome.service as service

logger = logging.getLogger(__name__)

try:
    API_KEY = os.environ['SHODAN_API_KEY']
except KeyError:
    try:
        API_KEY = open('SHODAN_API_KEY').read()
    except IOError:
        print ("Put your shodan API key in the environment with\n"
               "export SHODAN_API_KEY=yourkeyhere\n"
               "or put your key in a file named SHODAN_API_KEY.")
    exit()

QUERY = 'server: GoAhead-Webs login.asp'
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


@celery.task(soft_time_limit=300, time_limit=600)
def get_shodan_results(page=1):
    logger.info("Fetching shodan results page: %s", page)
    api = shodan.WebAPI(API_KEY)
    try:
        res = api.search(QUERY, page=page)
    except shodan.api.WebAPIError:
        logger.info('Finished shodan results with %s page(s).', page -1)
    else:
        get_shodan_results.delay(page=page+1)
        for r in res.get('matches', []):
            get_screenshot.delay(r)
        return res

class WebDriverTask(Task):
    abstract = True
    _driver = None

    @property
    def driver(self):
        if self._driver is None:
            self._driver = webdriver.Remote(
                service.service_url,
                desired_capabilities=options.to_capabilities())
        return self._driver

def dismiss_alerts(driver):
    # handle any possible blocking alerts
    alert = driver.switch_to_alert()
    try:
        alert.dismiss()
        logger.info(
            'Closed alert for %s: %s', driver.current_url, alert.text)
    except selenium.common.exceptions.NoAlertPresentException:
        pass


@celery.task(base=WebDriverTask)
def get_screenshot(result):
    ip = result['ip']
    try:
        driver = get_screenshot.driver
        driver.get('http://%s' % ip)
        dismiss_alerts(driver)
        logger.info('Loaded %s: %s' % (ip, driver.title))

        # this seems to require an absolute path for some reason
        driver.get_screenshot_as_file(os.path.join(os.getcwd(),
                                                   'out/%s.png' % ip))
        driver.get('about:blank')

    except exceptions.SoftTimeLimitExceeded:
        logger.info('Terminating overtime process')
    except Exception as e:
        print 'MAJOR PROBEM: ', ip
        print e
        raise


@signals.worker_shutdown.connect
def worker_shutdown(sender=None, conf=None, **kwargs):
    print sender, conf, kwargs
    sender.driver.quit()
    logger.info('Shutting down worker...')
    driver.quit()
    service.stop()
