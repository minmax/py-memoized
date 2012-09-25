from .storage_factory_container import storage_factory_container
from .errors import NoResult


def default_key(*args, **kwargs):
    if args or kwargs:
        raise TypeError('Args or KWargs not supported')


class CountingInvalidateFactory(object):
    pass


class Options(object):
    def __init__(self, function, storage, key, invalidate):
        self.function = function
        self.storage = storage
        self.key = key
        self.invalidate = invalidate


class KeyGenerator(object):
    def __init__(self, key=None):
        if key is None:
            self.key = None


class Memoizer(object):
    def __init__(self, function, storage, **kwargs):
        self.function = function
        storage = storage_factory_container.get_storage(storage, function, **kwargs)
        self.storage = storage

    def get_result(self, args, kwargs):
        try:
            return self.storage.get_result(args, kwargs)
        except NoResult:
            result = self.function(*args, **kwargs)
            self.storage.save_result(args, kwargs, result)
            return result


class ThreadSafeMemoizer(Memoizer):
    def get_result(self, args, kwargs):
        with self.storage.get_lock(args, kwargs):
            return super(ThreadSafeMemoizer, self).get_result(args, kwargs)
