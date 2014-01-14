from functools import wraps, update_wrapper

from .memoizer import Memoizer


def memoized(func=None, storage=None, **options):
    def decorator(function):
        cleanable = options.pop('cleanable', False)
        memoizer = Memoizer(function, storage, **options)

        @wraps(function)
        def wrapper(*args, **kwargs):
            return memoizer.get_result(args, kwargs)
        wrapper.memoizer = memoizer
        if cleanable:
            instance_wrapper = Wrapper(memoizer, wrapper)
            wrapper = update_wrapper(instance_wrapper, function)
        return wrapper
    return decorator if func is None else decorator(func)


class Wrapper(object):
    def __init__(self, memoizer, real_wrapper):
        self.memoizer = memoizer
        self.real_wrapper = real_wrapper

    def __call__(self, *args, **kwargs):
        return self.real_wrapper(*args, **kwargs)

    def __get__(self, instance, owner):
        if instance is None:
            return self.real_wrapper
        else:
            return BindedWrapper(self, instance)


class BindedWrapper(object):
    def __init__(self, wrapper, instance):
        """
        :type wrapper: Wrapper
        """
        self.__wrapper = wrapper
        self.__instance = instance

    def __call__(self, *args, **kwargs):
        return self.__wrapper.real_wrapper(self.__instance, *args, **kwargs)

    @property
    def memoizer(self):
        return MemoizerProxy(self.__wrapper.memoizer, self.__instance)


class MemoizerProxy(object):
    def __init__(self, memoizer, instance):
        self.__memoizer = memoizer
        self.__instance = instance

    def clear(self):
        self.__memoizer.clear(self.__instance)
