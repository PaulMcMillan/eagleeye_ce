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
