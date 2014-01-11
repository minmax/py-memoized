import time

from .invalidate import Expire, Count, Event
from .errors import CleanerNotDefined


class ExpireCleaner(object):
    timer = time.time

    def __init__(self, rule):
        self.rule = rule
        if rule.timer is not None:
            self.timer = rule.timer

    def is_missed(self):
        now = self.timer()
        if now >= self.created_at + self.rule.period:
            return True

    def after_fetch(self):
        self.created_at = self.timer()


class CountCleaner(object):
    def __init__(self, rule):
        self.rule = rule

    def is_missed(self):
        if self.readers_count >= self.rule.count:
            return True
        self.readers_count += 1

    def after_fetch(self):
        self.readers_count = 0


class EventCleaner(object):
    def __init__(self, rule):
        rule.listener.connect(self.clean)

    def clean(self):
        self.cleaned = True

    def is_missed(self):
        return self.cleaned

    def after_fetch(self):
        self.cleaned = False


class DummyCleaner(object):
    def is_missed(self):
        return False

    def after_fetch(self):
        pass


class CleanerFactory(object):
    cleaners = {
        Expire: ExpireCleaner,
        Count: CountCleaner,
        Event: EventCleaner,
    }

    dummy_cleaner = DummyCleaner()

    def get_cleaner(self, rule):
        if rule is None:
            return self.dummy_cleaner
        try:
            cleaner_cls = self.cleaners[type(rule)]
        except KeyError:
            raise CleanerNotDefined('No cleaner for %r' % (rule, ))
        else:
            return cleaner_cls(rule)
