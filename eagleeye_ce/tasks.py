import base64
import httplib
import logging
import os
import socket

import celery.exceptions as celery_exceptions
import pyvirtualdisplay
import selenium.common.exceptions
import selenium.webdriver.chrome.service as chrome_service
import shodan
from celery import Task
from selenium import webdriver

from eagleeye_ce import API_KEY
from eagleeye_ce import celery

logger = logging.getLogger(__name__)

socket.setdefaulttimeout(25)

# set up the xvfb display
display = pyvirtualdisplay.Display(visible=0, size=(600, 600))
display.start()

# Set up the webdriver options
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
        """ Things go wrong with the webdriver; we want to recover robustly """
        logger.info('Terminating webdriver.')

        # Don't quit the driver here because it often hangs
        self._driver = None

        if self._service is not None:
            try:
                self._service.stop()
            except Exception:
                # This is really bad...
                pass
        # throw away the old one no matter what
        self._service = None


@celery.task(base=WebDriverTask, soft_time_limit=300, time_limit=600)
def get_shodan_result(query, page=1):
    logger.info("Fetching shodan results query: %s page: %s", query, page)
    api = shodan.WebAPI(API_KEY)
    try:
        res = api.search(query, page=page)
    except shodan.api.WebAPIError:
        logger.info('Finished shodan results with %s page(s).', page - 1)
    else:
        if res:
            get_shodan_result.apply_async(args=[query],
                                           kwargs={'page': page + 1},
                                           queue='get_shodan_result')
        for r in res.get('matches', []):
            get_screenshot.apply_async(args=[r], queue='get_screenshot')
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

        write_screenshot.apply_async(
            args=[driver.get_screenshot_as_base64(), ip],
            queue='write_screenshot')

        # try going to a blank page so we get an error now if we can't
        driver.get('about:blank')
    except (celery_exceptions.SoftTimeLimitExceeded,
            socket.timeout):
        logger.info('Terminating overtime process: %s %s',
                    get_screenshot.request.id, ip)
        get_screenshot.terminate_driver()
    except (selenium.common.exceptions.WebDriverException,
            httplib.BadStatusLine):
        # just kill it, alright?
        get_screenshot.terminate_driver()
    except Exception as e:
        print repr(e)
        print 'MAJOR PROBLEM: ', ip, e
        get_screenshot.terminate_driver()


@celery.task
def write_screenshot(screenshot, ip):
    """ Separate task (and queue: write_screenshot) for writing the
    screenshots to disk, so it can be run wherever the results are
    desired.
    """
    binary_screenshot = base64.b64decode(screenshot)
    f = open(os.path.join(os.getcwd(), 'out/%s.png' % ip), 'w')
    f.write(binary_screenshot)
    f.close()
