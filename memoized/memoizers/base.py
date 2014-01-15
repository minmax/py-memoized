from ..storage_factory_factory import storage_factory_factory


class BaseMemoizer(object):
    storages = storage_factory_factory

    def __init__(self, function, storage, **kwargs):
        self.function = function
        storage = self.storages.get_storage(storage, function, **kwargs)
        self.storage = storage

    def get_result(self, *args, **kwargs):
        raise NotImplementedError()

    def clear(self, instance=None):
        self.storage.clear(instance)
