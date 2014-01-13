from .storage_factory_container import storage_factory_container
from .errors import NoResult


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

    def clear(self):
        self.storage.clear()
