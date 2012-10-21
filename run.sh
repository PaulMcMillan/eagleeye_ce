celery purge
celery call eagleeye_ce.tasks.get_shodan_results
celery -A eagleeye_ce.tasks worker --loglevel=info