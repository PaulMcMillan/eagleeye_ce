import logging
import os

from celery import Celery

import eagleeye_ce.settings_default

logger = logging.getLogger(__name__)

celery = Celery('tasks')
celery.config_from_object(eagleeye_ce.settings_default)


# Try to load any local settings file
try:
    import settings as user_settings
except ImportError:
    pass
else:
    logger.debug('Loaded local settings file.')
    celery.config_from_object(user_settings, silent=True)

# Make sure we have a shodan API key
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
