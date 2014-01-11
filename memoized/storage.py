from .errors import NoResult
from .cleaners import CleanerFactory


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


class BaseContainerStrategy(object):
    def __init__(self, storage_strategy):
        self.storage_strategy = storage_strategy


class FunctionContainerStrategy(BaseContainerStrategy):
    def __init__(self, storage_strategy):
        super(FunctionContainerStrategy, self).__init__(storage_strategy)
        self.function = storage_strategy.storage.function

    def get_object(self, args, kwargs):
        return self.function


class InstanceContainerStrategy(BaseContainerStrategy):
    def get_object(self, args, kwargs):
        return args[0]


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


class BaseHolderStrategy(object):
    def __init__(self, storage_strategy):
        self.attr_name = storage_strategy.attr_name


class FunctionHolderStrategy(BaseHolderStrategy):
    def __init__(self, storage_strategy):
        super(FunctionHolderStrategy, self).__init__(storage_strategy)
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


class InstanceHolderStrategy(BaseHolderStrategy):
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
            return container


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
        return InstanceContainerStrategy(strategy)

    def get_holder(self, strategy):
        return InstanceHolderStrategy(strategy)


class FunctionStorageFactory(BaseStorageFactory):
    def get_container(self, strategy):
        return FunctionContainerStrategy(strategy)

    def get_holder(self, strategy):
        return FunctionHolderStrategy(strategy)
