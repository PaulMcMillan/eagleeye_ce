celery purge
celery call eagleeye2.tasks.get_shodan_results
celery -A eagleeye2.tasks worker --loglevel=info --soft-time-limit=30 --time-limit=45 --concurrency=3
