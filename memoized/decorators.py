from functools import wraps, update_wrapper

from .memoizers.simple_memoizer import SimpleMemoizer
from .memoizers.tx_memoizer import TxMemoizer
from .memoizers.tornado_memoizer import TornadoMemoizer


def memoized_decorator_factory(memoizer_cls):
    def memoized(func=None, storage=None, **options):
        def decorator(function):
            cleanable = options.pop('cleanable', False)
            memoizer = memoizer_cls(function, storage, **options)

            @wraps(function)
            def wrapper(*args, **kwargs):
                return memoizer.get_result(*args, **kwargs)
            wrapper.memoizer = memoizer
            if cleanable:
                instance_wrapper = Wrapper(memoizer, wrapper)
                wrapper = update_wrapper(instance_wrapper, function)
            return wrapper
        return decorator if func is None else decorator(func)
    return memoized


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


memoized = memoized_decorator_factory(SimpleMemoizer)
tx_memoized = memoized_decorator_factory(TxMemoizer)
task_memoized = memoized_decorator_factory(TornadoMemoizer)
