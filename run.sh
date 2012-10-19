celery purge
celery call tasks.get_shodan_results
celery -A tasks worker --loglevel=info --concurrency=2 --soft-time-limit=10 --time-limit=25
