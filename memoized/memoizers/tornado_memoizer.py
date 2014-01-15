try:
    from tornado import gen
    tornado_support = True
except ImportError:
    class _Gen(object):
        engine = staticmethod(lambda function: function)
    gen = _Gen()
    del _Gen
    tornado_support = False

from ..errors import NoResult, ImproperlyConfigured
from .base import BaseMemoizer


class TornadoMemoizer(BaseMemoizer):
    def __init__(self, function, storage, **kwargs):
        super(TornadoMemoizer, self).__init__(function, storage, **kwargs)
        if not tornado_support:
            raise ImproperlyConfigured('Cant find tornado')

    @gen.engine
    def get_result(self, *args, **kwargs):
        callback = kwargs.pop('callback', None)
        try:
            result = self.storage.get_result(args, kwargs)
        except NoResult:
            result = yield gen.Task(self.function, *args, **kwargs)
            self.storage.save_result(args, kwargs, result)

        if callback is not None:
            callback(result)
