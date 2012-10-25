import os
import signal
import logging
import subprocess
from pyvirtualdisplay import Display
from selenium import webdriver
import selenium
import httplib
import shodan
from celery import Celery
from celery import group
from celery import exceptions
from celery import Task
from celery import signals
import selenium.webdriver.chrome.service as chrome_service

import cleanup

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

QUERY = 'org:cern'
celery = Celery('tasks')
celery.config_from_object('celeryconfig')


# set up the xvfb display
display = Display(visible=0, size=(600, 600))
display.start()


# Set up the webdriver
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
options.add_argument('--disable-java')
options.add_argument('--incognito')
options.add_argument('--use-mock-keychain')
#options.add_argument('--kiosk')
# http://peter.sh/experiments/chromium-command-line-switches/


class WebDriverTask(Task):
    abstract = True
    _driver = None
    _service = None

    @property
    def service(self):
        if self._service is None:
            self._service = chrome_service.Service('chromedriver')
            self._service.start()
        return self._service

    @property
    def driver(self):
        if self._driver is None:
            self._driver = webdriver.Remote(
                self.service.service_url,
                desired_capabilities=options.to_capabilities())
        return self._driver

    def terminate_driver(self):
        logger.info('Terminating webdriver.')
        # Yeah... things go wrong here, we want to recover robustly.
        try:
            if self._driver:
                # Don't quit the driver here because it often hangs
                print "stopped driver."
                self._driver = None
        except Exception:
            # cringe... but shit goes wrong often
            pass

        try:
            if self._service:
                self._service.stop()
                self._service = None
        except Exception:
            #yeee
            pass

    def task_cleanup(self):
        # do we need this now?
        pass


@celery.task(base=WebDriverTask, soft_time_limit=300, time_limit=600)
def get_shodan_results(page=1):
    logger.info("Fetching shodan results page: %s", page)
    api = shodan.WebAPI(API_KEY)
    try:
        res = api.search(QUERY, page=page)
    except shodan.api.WebAPIError:
        logger.info('Finished shodan results with %s page(s).', page -1)
    else:
        if res:
            get_shodan_results.delay(page=page+1)
        for r in res.get('matches', []):
            get_screenshot.delay(r)
        return res


def dismiss_alerts(driver):
    # handle any possible blocking alerts because selenium is stupid
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
    logger.info('Loading %s %s', get_screenshot.request.id, ip)
    try:
        driver = get_screenshot.driver
        driver.get('http://%s' % ip)
        dismiss_alerts(driver)
        logger.info('Loaded %s: %s' % (ip, driver.title))

        # this seems to require an absolute path for some reason
        driver.get_screenshot_as_file(os.path.join(os.getcwd(),
                                                   'out/%s.png' % ip))
        # try going to a blank page so we get an error now if we can't
        driver.get('about:blank')
    except exceptions.SoftTimeLimitExceeded:
        logger.info('Terminating overtime process: %s %s',
                    get_screenshot.request.id, ip)
        get_screenshot.terminate_driver()
    except (selenium.common.exceptions.WebDriverException,
            httplib.BadStatusLine):
        # just kill it, alright?
        get_screenshot.terminate_driver()
#    except cleanup.CleanupException:
#        pass
    except Exception as e:
        print repr(e)
        print 'MAJOR PROBEM: ', ip, e
        get_screenshot.terminate_driver()
        #raise


@signals.worker_shutdown.connect
def worker_shutdown(sender=None, conf=None, **kwargs):
    logger.info('Shutting down worker...')
