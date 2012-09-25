from datetime import timedelta


class EventListener(object):
    callback = None

    def connect(self, callback):
        self.callback = callback

    def clean(self):
        assert self.callback is not None, '%r not connected' % self
        self.callback()


class Event(object):
    def __init__(self, listener):
        self.listener = listener


class Count(object):
    def __init__(self, count):
        self.count = count


class Expire(object):
    def __init__(self, period, timer=None):
        if isinstance(period, timedelta):
            period = period.total_seconds()
        assert period >= 0, 'Period must be >=0, not %r' % (period, )
        self.period = period
        self.timer = timer
