celery purge
./send_job.py
celery -A eagleeye_ce.tasks worker --loglevel=info