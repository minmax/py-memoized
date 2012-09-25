py-memoized
===========

Powerful python memoized decorator

```
from memoized import memoized
from memoized.const import SELF, FUNCTION
from memoized.invalidate import Expire


class Foo(object):
    @memoized(storage=SELF, invalidate=Expire(60))
    def get_some_data(self):
        return 'foo'


@memoized(storage=FUNCTION, key=lambda p: p.id)
def get_profile_balance(profile):
    return Balance.get_for_profile(profile)
```
