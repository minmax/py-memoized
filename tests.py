import sys

from unittest2 import TestCase

from mock import Mock

from memoized import memoized
from memoized.invalidate import Count, Expire, Event, EventListener
from memoized.const import SELF, FUNCTION
from memoized.cleaners import CleanerFactory, DummyCleaner, CountCleaner, ExpireCleaner, EventCleaner
from memoized.errors import CleanerNotDefined


class CleanerTest(TestCase):
    def test_count_cleaner(self):
        cleaner = CountCleaner(Count(1))
        cleaner.after_fetch()
        self.assertFalse(cleaner.is_missed())
        self.assertTrue(cleaner.is_missed())

    def test_expire_cleaner(self):
        timer = Mock(return_value=0)
        cleaner = ExpireCleaner(Expire(2, timer))
        cleaner.after_fetch()
        timer.return_value = 1
        self.assertFalse(cleaner.is_missed())
        timer.return_value = 2
        self.assertTrue(cleaner.is_missed())

    def test_event_cleaner(self):
        listener = EventListener()
        cleaner = EventCleaner(Event(listener))
        cleaner.after_fetch()
        self.assertFalse(cleaner.is_missed())
        listener.clean()
        self.assertTrue(cleaner.is_missed())


class BaseTest(TestCase):
    data = 'test'

    def increment_calls_count(self):
        self.calls_count += 1

    def assertDataGeneratorCalled(self, count):
        self.assertEqual(count, self.calls_count)

    def setUp(self):
        self.calls_count = 0

    def call_twice(self, function, result=data):
        self.call_with_check_result(function, result)
        self.call_with_check_result(function, result)

    def call_with_check_result(self, func, result=data):
        self.assertEqual(result, func())

    def create_function(self, return_value=data, storage=FUNCTION, **kwargs):
        @memoized(storage=storage, **kwargs)
        def func():
            self.increment_calls_count()
            return return_value
        return func

    def create_instance(self, return_value=data, **kwargs):
        cls = self.create_cls(return_value, **kwargs)
        return cls()

    def create_cls(self, return_value=data, **kwargs):
        test = self

        options = {
            'storage': SELF,
        }
        options.update(kwargs)

        class NewClass(object):
            @memoized(**options)
            def do(self, *args, **kwargs):
                test.increment_calls_count()
                return return_value
        return NewClass


class InvalidateTests(BaseTest):
    def test_expire_after_2_calls(self):
        func = self.create_function(invalidate=Count(2))
        self.call_twice(func)
        self.call_with_check_result(func)
        self.assertDataGeneratorCalled(1)
        self.call_with_check_result(func)
        self.assertDataGeneratorCalled(2)

    def test_expire_after_timeout(self):
        mock_timer = Mock(return_value=0)
        func = self.create_function(invalidate=Expire(2, timer=mock_timer))
        self.call_twice(func)
        self.assertDataGeneratorCalled(1)
        mock_timer.return_value = 3
        self.call_with_check_result(func)
        self.assertDataGeneratorCalled(2)


class BaseStorageTest(BaseTest):
    def check_cache_worked(self, function):
        self.call_twice(function)
        self.assertDataGeneratorCalled(1)


class InstanceStorageTests(BaseStorageTest):
    def test_cache_worked(self):
        obj = self.create_instance(return_value=self.data)
        self.check_cache_worked(obj.do)

    def test_cache_local_to_one_instance(self):
        obj1 = self.create_instance(return_value=1)
        obj2 = self.create_instance(return_value=2)
        self.call_with_check_result(obj1.do, 1)
        self.call_with_check_result(obj2.do, 2)
        self.assertDataGeneratorCalled(2)


class FunctionStorageTest(BaseStorageTest):
    def test_cache_worked(self):
        func = self.create_function()
        self.check_cache_worked(func)

    def test_two_functions_has_different_caches(self):
        func1 = self.create_function(return_value=1)
        func2 = self.create_function(return_value=2)
        self.call_twice(func1, 1)
        self.call_twice(func2, 2)
        self.assertDataGeneratorCalled(2)


class CleanerFactoryTest(TestCase):
    def setUp(self):
        self.factory = CleanerFactory()

    def test_dummy_cleaner(self):
        cleaner = self.factory.get_cleaner(None)
        self.assertIsInstance(cleaner, DummyCleaner)

    def test_count_cleaner(self):
        cleaner = self.factory.get_cleaner(Count(0))
        self.assertIsInstance(cleaner, CountCleaner)

    def test_not_registered_cleaner(self):
        with self.assertRaises(CleanerNotDefined):
            self.factory.get_cleaner(object())


class CleanTest(BaseTest):
    def test_function_no_key(self):
        @memoized(storage=FUNCTION)
        def func():
            self.increment_calls_count()
        self.call_twice_and_check_calls_count(func)

    def test_function_with_key(self):
        @memoized(storage=FUNCTION, key=lambda x: id(x))
        def func(obj):
            self.increment_calls_count()
        self.call_twice_and_check_calls_count(func, object())

    def test_instance_no_key(self):
        obj = self.create_instance()
        self.call_twice_and_check_calls_count(obj.do)

    def test_instance_with_key(self):
        obj = self.create_instance(key=lambda s, x: id(x))
        self.call_twice_and_check_calls_count(obj.do, object())

    def call_twice_and_check_calls_count(self, func, *args, **kwargs):
        func(*args, **kwargs)
        self.assertEqual(1, self.calls_count)
        func.memoizer.clear()
        func(*args, **kwargs)
        self.assertEqual(2, self.calls_count)

    def test_no_refs_for_collected_objects(self):
        obj = self.create_instance()
        refs_count = sys.getrefcount(obj)
        obj.do()
        self.assertEqual(sys.getrefcount(obj), refs_count)
