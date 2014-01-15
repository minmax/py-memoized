from ..errors import NoResult
from .base import BaseMemoizer


class SimpleMemoizer(BaseMemoizer):
    def get_result(self, *args, **kwargs):
        try:
            return self.storage.get_result(args, kwargs)
        except NoResult:
            result = self.function(*args, **kwargs)
            self.storage.save_result(args, kwargs, result)
            return result
