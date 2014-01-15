try:
    from twisted.internet.defer import inlineCallbacks, returnValue
    twisted_support = True
except ImportError:
    inlineCallbacks = lambda function: function
    twisted_support = False

from ..errors import NoResult, ImproperlyConfigured
from .base import BaseMemoizer


class TxMemoizer(BaseMemoizer):
    def __init__(self, function, storage, **kwargs):
        super(TxMemoizer, self).__init__(function, storage, **kwargs)
        if not twisted_support:
            raise ImproperlyConfigured('Cant find twisted')

    @inlineCallbacks
    def get_result(self, *args, **kwargs):
        try:
            result = self.storage.get_result(args, kwargs)
        except NoResult:
            result = yield self.function(*args, **kwargs)
            self.storage.save_result(args, kwargs, result)
        returnValue(result)
