__author__ = 'sasaki'
isiterable = lambda obj: isinstance(obj, basestring) or hasattr(obj, '__iter__')


def isEqualIfExists(o1, o2, a):
    if not hasattr(o1, a) and not hasattr(o2, a): return True
    if not hasattr(o1, a): return False
    if not hasattr(o2, a): return False
    if o1.a != o2.a: return False
    return True
