# Ideas from: http://stackoverflow.com/a/8230470/114917

import logging

from celery import current_app
from celery import platforms
from celery.signals import worker_process_init
from time import sleep
from celery.worker import state

logger = logging.getLogger(__name__)

class CleanupException(Exception):
    """ Exception raised during cleanup """

def cleanup_after_tasks(signum, frame):
    task_list = current_app.tasks
    for task_name, task_function in task_list.items():
        if hasattr(task_function, 'task_cleanup'):
            logger.info('Cleaning up %s for shutdown', task_name)
            task_function.task_cleanup()
            raise CleanupException()

def install_pool_process_sighandlers(**kwargs):
    platforms.signals["TERM"] = cleanup_after_tasks
    platforms.signals["INT"] = cleanup_after_tasks

#worker_process_init.connect(install_pool_process_sighandlers)
