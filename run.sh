celeryctl purge
celery -A tasks worker --loglevel=info --concurrency=2 --soft-time-limit=10 --time-limit=25
python tasks.py