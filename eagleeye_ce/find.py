import logging

import shodan
from eagleeye_ce import celery
from eagleeye_ce import API_KEY

logger = logging.getLogger(__name__)

@celery.task(soft_time_limit=30, time_limit=60)
def get_shodan_result(query, page=1):
    logger.info("Fetching shodan results query: %s page: %s", query, page)
    api = shodan.WebAPI(API_KEY)
    return api.search(query, page=page)['matches']
