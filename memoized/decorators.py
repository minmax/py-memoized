from functools import wraps

from .memoizer import Memoizer


def memoized(function=None, storage=None, **kwargs):
    def decorator(function):
        memoizer = Memoizer(function, storage, **kwargs)

        @wraps(function)
        def wrapper(*args, **kwargs):
            return memoizer.get_result(args, kwargs)
        return wrapper
    return decorator if function is None else decorator(function)
