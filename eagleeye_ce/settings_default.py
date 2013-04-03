# You might want to modify this stuff
BROKER_URL = 'amqp://'
CELERYD_CONCURRENCY = 10
CELERYD_TASK_SOFT_TIME_LIMIT = 30
CELERYD_TASK_TIME_LIMIT = 45

# You probably don't want to modify the stuff below this line
CELERYD_PREFETCH_MULTIPLIER = 1
# This is to handle https://github.com/celery/celery/pull/969
CELERY_ACKS_LATE = True

CELERY_RESULT_BACKEND = "amqp"
