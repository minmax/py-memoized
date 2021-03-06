from .const import SELF, FUNCTION
from .storage import FunctionStorageFactory, InstanceStorageFactory


class StorageFactoryFactory(object):
    def __init__(self):
        self.storages = {
            SELF: InstanceStorageFactory(),
            FUNCTION: FunctionStorageFactory(),
        }

    def get_storage(self, name, function, **kwargs):
        if isinstance(name, basestring):
            storage_factory = self.storages[name]
            return storage_factory(function, **kwargs)
        else:
            return name


storage_factory_factory = StorageFactoryFactory()
