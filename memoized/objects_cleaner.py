from weakref import WeakSet


class ObjectsCleaner(object):
    def __init__(self, attribute_name):
        self.attribute_name = attribute_name
        self.objects = WeakSet()

    def add(self, obj):
        self.objects.add(obj)

    def clear(self):
        for obj in self.objects:
            print 'REMOVE', obj
            try:
                delattr(obj, self.attribute_name)
            except AttributeError:
                pass
        self.objects.clear()
