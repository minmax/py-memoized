from importlib import import_module

from .const import SELF, FUNCTION


STORAGE_FACTORY_MAP = {
    SELF: '.storage:InstanceStorageFactory',
    FUNCTION: '.storage:FunctionStorageFactory',
}


class StorageFactoryContainer(object):
    def __init__(self):
        self.storage_factory_by_name = {}
        self.storage_factory_cls_map = STORAGE_FACTORY_MAP.copy()

    def register(self, name, storage):
        self.storage_factory_cls_map[name] = storage

    def get_storage(self, name, function, **kwargs):
        storage_factory = self._get_storage_factory_by_name(name)
        return storage_factory(function, **kwargs)

    def _get_storage_factory_by_name(self, name):
        try:
            return self.storage_factory_by_name[name]
        except KeyError:
            pass

        storage_factory = self._get_storage_factory_instance(name)
        self.storage_factory_by_name[name] = storage_factory
        return storage_factory

    def _get_storage_factory_instance(self, name):
        cls_path = self.storage_factory_cls_map[name]
        if isinstance(cls_path, basestring):
            module_path, attr_name = cls_path.split(':')
            cls_module = import_module(module_path, __package__)
            instance_or_cls = getattr(cls_module, attr_name)
        else:
            instance_or_cls = cls_path

        if isinstance(instance_or_cls, type):
            return instance_or_cls()
        else:
            return instance_or_cls


storage_factory_container = StorageFactoryContainer()
