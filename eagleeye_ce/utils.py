import functools

from celery import current_task

def iterit(*args, **kwargs):
    """
    This takes some input (int, string, list, iterable, whatever) and
    makes sure it is an iterable, making it a single item list if not.
    Importantly, it does rational things with strings.

    You can pass it more than one item. Cast is optional.

    def foo(offsets=10):
        offsets = iterit(offsets, cast=int)
        for f in offsets:
            print "Value %s" % (10 + f)

    >>> foo()
    Value 20
    >>> foo(3)
    Value 13
    >>> foo([1,2])
    Value 11
    Value 12
    >>> foo('3')
    Value 13
    >>> foo(('3', 4))
    Value 13
    Value 14

    Also useful this way:
    foo, bar = iterit(foo, bar)
    """
    if len(args) > 1:
        return [iterit(arg, **kwargs) for arg in args]
    return map(kwargs.get('cast', None),
               args[0] if hasattr(args[0], '__iter__') else [args[0], ])


# Use this wrapper with functions in chains that return a tuple. The
# next function in the chain will get called with that the contents of
# tuple as (first) positional args, rather than just as just the first
# arg. Note that both the sending and receiving function must have
# this wrapper, which goes between the @task decorator and the
# function definition. This wrapper should not otherwise interfere
# when these conditions are not met.

class UnwrapMe(object):
    def __init__(self, contents):
        self.contents = contents

    def __call__(self):
        return self.contents

def wrap_for_chain(f):
    """ Too much deep magic. """
    @functools.wraps(f)
    def _wrapper(*args, **kwargs):
        if type(args[0]) == UnwrapMe:
            args = list(args[0]()) + list(args[1:])
        result = f(*args, **kwargs)

        if type(result) == tuple and current_task.request.callbacks:
            return UnwrapMe(result)
        else:
            return result
    return _wrapper
