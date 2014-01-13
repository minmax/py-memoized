from weakref import WeakSet


class ObjectsCleaner(object):
    def __init__(self, attribute_name):
        self.attribute_name = attribute_name
        self.objects = WeakSet()

    def add(self, obj):
        self.objects.add(obj)

    def clear(self, instance=None):
        if instance is None:
            self._clear_all_objects()
        else:
            self._clear_obj(instance)
            try:
                self.objects.remove(instance)
            except KeyError:
                pass

    def _clear_all_objects(self):
        for obj in self.objects:
            self._clear_obj(obj)
        self.objects.clear()

    def _clear_obj(self, obj):
        try:
            delattr(obj, self.attribute_name)
        except AttributeError:
            pass
