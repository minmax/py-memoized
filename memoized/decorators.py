from functools import wraps

from .memoizer import Memoizer, ThreadSafeMemoizer


def memoized(function=None, ts=False, storage=None, **kwargs):
    def decorator(function):
        if ts:
            memoizer = ThreadSafeMemoizer(function, storage, **kwargs)
        else:
            memoizer = Memoizer(function, storage, **kwargs)

        @wraps(function)
        def wrapper(*args, **kwargs):
            return memoizer.get_result(args, kwargs)
        return wrapper
    return decorator if function is None else decorator(function)
