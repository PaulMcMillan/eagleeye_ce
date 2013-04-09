import base64
import httplib
import logging
import os

import celery.exceptions as celery_exceptions
import pyvirtualdisplay
import selenium.common.exceptions
import selenium.webdriver.chrome.service as chrome_service

from celery import Task
from selenium import webdriver

from eagleeye_ce import celery
from eagleeye_ce import nmap
from eagleeye_ce import utils

logger = logging.getLogger(__name__)

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
                pgroup = os.getpgid(self._service.process.pid)
                # os.killpg(pgroup, ) # XXX

            except Exception:
                # This is really bad...
                pass

        # throw away the old one no matter what
        self._service = None


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
@utils.wrap_for_chain
def get_screenshot(host, port='80', proto='http'):
    target_url = '%s://%s:%s' % (proto, host, port)
    logger.info('Loading %s', target_url)
    screenshot = None
    try:
        driver = get_screenshot.driver
        driver.get(target_url)
        dismiss_alerts(driver)
        logger.info('Loaded %s' % target_url)

        screenshot = driver.get_screenshot_as_base64()

        # try going to a blank page so we get an error now if we can't
        driver.get('about:blank')
    except celery_exceptions.SoftTimeLimitExceeded:
        logger.info('Terminating overtime process: %s', target_url)
        get_screenshot.terminate_driver()
    except (selenium.common.exceptions.WebDriverException,
            httplib.BadStatusLine):
        # just kill it, alright?
        get_screenshot.terminate_driver()
    except Exception as e:
        print repr(e)
        print 'MAJOR PROBLEM: ', target_url
        get_screenshot.terminate_driver()
    if screenshot:
        return screenshot, target_url


@celery.task
@utils.wrap_for_chain
def write_screenshot(screenshot, url):
    """ Separate task (and queue: write_screenshot) for writing the
    screenshots to disk, so it can be run wherever the results are
    desired.
    """
    binary_screenshot = base64.b64decode(screenshot)
    file_name = url.replace('://', '_').replace(':', '_')
    f = open(os.path.join(os.getcwd(), 'out/%s.png' % file_name), 'w')
    f.write(binary_screenshot)
    f.close()
