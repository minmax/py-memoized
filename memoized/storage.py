from .errors import NoResult
from .cleaners import CleanerFactory
from .objects_cleaner import ObjectsCleaner


class SimpleStorage(object):
    cleaner_factory = CleanerFactory()
    strategy = None

    def __init__(self, function, invalidate=None, key=None, **kwargs):
        assert not kwargs, '%r not supported' % kwargs
        self.function = function
        self.key = key
        self.invalidate = self.cleaner_factory.get_cleaner(invalidate)

    def get_result(self, args, kwargs):
        result = self.strategy.get_result(args, kwargs)
        if self.invalidate.is_missed():
            raise NoResult()
        return result

    def save_result(self, args, kwargs, result):
        self.invalidate.after_fetch()
        self.strategy.save_result(args, kwargs, result)

    def clear(self, instance=None):
        self.strategy.clear(instance)


class SimpleStorageStrategy(object):
    container = None

    def __init__(self, storage):
        self.storage = storage
        self.attr_name = '_memoized_result_%s' % self.storage.function.__name__

    def get_result(self, args, kwargs):
        try:
            return getattr(self.container.get_object(args, kwargs), self.attr_name)
        except AttributeError:
            raise NoResult()

    def save_result(self, args, kwargs, result):
        setattr(self.container.get_object(args, kwargs), self.attr_name, result)

    def clear(self, instance=None):
        self.container.clear(instance)


class StorageWithKeyStrategy(object):
    holder = None

    def __init__(self, storage):
        self.storage = storage
        self.attr_name = '_memoized_container_%s' % self.storage.function.__name__
        self.key = storage.key

    def get_result(self, args, kwargs):
        container = self.holder.get_container(args, kwargs)
        try:
            return container[self.key(*args, **kwargs)]
        except KeyError:
            raise NoResult()

    def save_result(self, args, kwargs, result):
        container = self.holder.get_or_create_container(args, kwargs)
        container[self.key(*args, **kwargs)] = result

    def clear(self, instance=None):
        self.holder.clear(instance)


class BaseContainerGetter(object):
    def __init__(self, storage_strategy):
        self.storage_strategy = storage_strategy


class FunctionContainerGetter(BaseContainerGetter):
    def __init__(self, storage_strategy):
        super(FunctionContainerGetter, self).__init__(storage_strategy)
        self.function = storage_strategy.storage.function

    def get_object(self, args, kwargs):
        return self.function

    def clear(self, instance=None):
        try:
            delattr(self.function, self.storage_strategy.attr_name)
        except AttributeError:
            pass


class InstanceContainerGetter(BaseContainerGetter):
    def __init__(self, storage_strategy):
        super(InstanceContainerGetter, self).__init__(storage_strategy)
        self.cleaner = ObjectsCleaner(storage_strategy.attr_name)

    def get_object(self, args, kwargs):
        instance = args[0]
        self.cleaner.add(instance)
        return instance

    def clear(self, instance=None):
        self.cleaner.clear(instance)


class BaseHolder(object):
    def __init__(self, storage_strategy):
        self.attr_name = storage_strategy.attr_name


class FunctionHolder(BaseHolder):
    def __init__(self, storage_strategy):
        super(FunctionHolder, self).__init__(storage_strategy)
        self.function = storage_strategy.storage.function

    def get_container(self, args, kwargs):
        try:
            return getattr(self.function, self.attr_name)
        except AttributeError:
            raise NoResult()

    def get_or_create_container(self, args, kwargs):
        try:
            return getattr(self.function, self.attr_name)
        except AttributeError:
            container = {}
            setattr(self.function, self.attr_name, container)
            return container

    def clear(self, instance=None):
        try:
            delattr(self.function, self.attr_name)
        except AttributeError:
            pass


class InstanceHolder(BaseHolder):
    def __init__(self, storage_strategy):
        super(InstanceHolder, self).__init__(storage_strategy)
        self.cleaner = ObjectsCleaner(self.attr_name)

    def get_container(self, args, kwargs):
        instance = args[0]
        try:
            return getattr(instance, self.attr_name)
        except AttributeError:
            raise NoResult()

    def get_or_create_container(self, args, kwargs):
        instance = args[0]
        try:
            return getattr(instance, self.attr_name)
        except AttributeError:
            container = {}
            setattr(instance, self.attr_name, container)
            self.cleaner.add(instance)
            return container

    def clear(self, instance=None):
        self.cleaner.clear(instance)


class BaseStorageFactory(object):
    def __call__(self, function, key=None, **kwargs):
        storage = SimpleStorage(function, key=key, **kwargs)
        if key is None:
            strategy = SimpleStorageStrategy(storage)
            strategy.container = self.get_container(strategy)
        else:
            strategy = StorageWithKeyStrategy(storage)
            strategy.holder = self.get_holder(strategy)
        storage.strategy = strategy
        return storage

    def get_container(self, strategy):
        raise NotImplementedError()

    def get_holder(self, strategy):
        raise NotImplementedError()


class InstanceStorageFactory(BaseStorageFactory):
    def get_container(self, strategy):
        return InstanceContainerGetter(strategy)

    def get_holder(self, strategy):
        return InstanceHolder(strategy)


class FunctionStorageFactory(BaseStorageFactory):
    def get_container(self, strategy):
        return FunctionContainerGetter(strategy)

    def get_holder(self, strategy):
        return FunctionHolder(strategy)
