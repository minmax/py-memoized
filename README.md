py-memoized
===========

Powerful python memoized decorator

```
from memoized import memoized
from memoized.const import SELF, FUNCTION


class Foo(object):
    @memoized(storage=SELF)
    def get_some_data(self):
        return 'foo'


@memoized(storage=FUNCTION, key=lambda p: p.id)
def get_profile_balance(profile):
    return Balance.get_for_profile(profile)
```


Clear cache:
```
# Function cache cleanup
get_profile_balance.memoizer.clear()

# All instances cache cleanup
Foo.get_some_data.memoizer.clear()
```

For cleanup only one instance cache, you must specify flag ```cleanable```. And it adds some little overhead.
```
class Foo(object):
    @memoized(storage=SELF, cleanable=True)
    def do(self):
        pass

foo = Foo()
# This cleans only one instance cache
foo.do.memoizer.clear()
```
