from unittest import TestCase

from mock import Mock

from memoized import memoized
from memoized.invalidate import Count, Expire
from memoized.const import SELF, FUNCTION


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

    def create_instance(self, return_value):
        test = self
        class NewClass(object):
            @memoized(storage=SELF)
            def do(self):
                test.increment_calls_count()
                return return_value
        return NewClass()


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
