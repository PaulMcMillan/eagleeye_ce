import requests
from celery import Task
from celery import states

TIMEOUT = 15
conf = {'keep_alive': False,
        'danger_mode': True,
        'store_cookies': False,
        # Maybe set the UA too
        }

from eagleeye_ce import celery
from time import sleep

import celery.exceptions as ce
from functools import wraps

def error_catcher(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            res = f(*args, **kwargs)
        except Exception:
            print "Exception!"
            return (False, args, kwargs)
        else:
            print "not exception!"
            return (True, args, kwargs)
    return wrapper

def add_error(chain, f):
    for c in chain:
        c.link_error(f.s())

@celery.task
def final(url):
    print url
    print "Final Boss!"

@celery.task
def doit(url):
    func_list = [head_request.s('http' + url),
                 get_request.s('http' + url),
                 head_request.s('https' + url),
                 get_request.s('https' + url)]
    first = func_list[0]
    while func_list:
        current = func_list.pop()
        print dir(current)
#        current.s(foo='bar')
        current.func_final = final
        if func_list:
            current.func_next = func_list[0]
    first.delay()

class ValidationTask(Task):
    func_next = None
    func_final = None

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        print retval
        print dir(self.request)
        success, args, kwargs = retval
        if success:
            self.func_final.delay()
        elif self.func_next:
            self.func_next.delay()
        else:
            print "No success, end of chain"

        super(ValidationTask, self).after_return(
            status, retval, task_id, args, kwargs, einfo)


@celery.task(base=ValidationTask)
@error_catcher
def head_request(url):
    print "head request " + url
    requests.head(url, timeout=TIMEOUT, config=conf, verify=False)
    return head_request

head_request.on_failure = lambda *a, **kw: Exception('whoah!')

@celery.task(base=ValidationTask)
@error_catcher
def get_request(url):
    print "get request " + url
    requests.get(url, timeout=TIMEOUT, config=conf, verify=False)
    return get_request

#get_request.on_failure = lambda e: "failed"
