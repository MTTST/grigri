from datetime import datetime, date

import unittest

import pandas as pd

from ..dates import scalar
from ..dates.scalar import strip_time, first_of, end_of, prorate

from ..dates.range import day_range



class TestScalarFunctions(unittest.TestCase):
    def test_strip_time_removes_time(self):
        dt = datetime(2000, 1, 1, 1, 1, 1)
        expected = datetime(2000, 1, 1)
        result = strip_time(dt)
        self.assertEqual(expected, result)

    def test_strip_time_upcasts_date(self):
        dt = date(2000, 1, 1)
        expected = datetime(2000, 1, 1)
        result = strip_time(dt)
        self.assertEqual(expected, result)

    def test_first_of(self):
        dt = datetime(2000, 5, 16, 1, 1, 1)

        # first of week should return monday
        # of given week
        result = first_of(dt, 'w')
        expected = datetime(2000, 5, 15)
        self.assertEqual(result, expected)
        self.assertEqual(result, scalar.first_of_week(dt))

        result = first_of(dt, 'm')
        expected = datetime(2000, 5, 1)
        self.assertEqual(result, expected)
        self.assertEqual(result, scalar.first_of_month(dt))

        result = first_of(dt, 'q')
        expected = datetime(2000, 4, 1)
        self.assertEqual(result, expected)
        self.assertEqual(result, scalar.first_of_quarter(dt))

        result = first_of(dt, 'y')
        expected = datetime(2000, 1, 1)
        self.assertEqual(result, expected)
        self.assertEqual(result, scalar.first_of_year(dt))

    def test_end_of(self):
        dt = datetime(2000, 5, 16, 1, 1, 1)

        # end of week should be the monday in the next week
        result = end_of(dt, 'w')
        expected = datetime(2000, 5, 22)
        self.assertEqual(result, expected)
        self.assertEqual(result, scalar.end_of_week(dt))

        result = end_of(dt, 'm')
        expected = datetime(2000, 5, 31)
        self.assertEqual(result, expected)
        self.assertEqual(result, scalar.end_of_month(dt))

        result = end_of(dt, 'q')
        expected = datetime(2000, 6, 30)
        self.assertEqual(result, expected)
        self.assertEqual(result, scalar.end_of_quarter(dt))

        result = end_of(dt, 'y')
        expected = datetime(2000, 12, 31)
        self.assertEqual(result, expected)
        self.assertEqual(result, scalar.end_of_year(dt))

        # test case when datetime is actually past end of month
        # date, but still in current month
        dt = datetime(2000, 7, 31, 10, 15)
        result = end_of(dt, 'm')
        expected = datetime(2000, 7, 31)
        self.assertEqual(result, expected)

    def test_prorate(self):
        result = prorate(datetime(2013,9, 26), 'm')
        expected = 26 / 30
        self.assertEqual(result, expected)

        # final day should prorate to 100%
        result = prorate(datetime(2013,9, 30), 'm')
        expected = 1.0
        self.assertEqual(result, expected)

        # first day should not prorate to 0%
        result = prorate(datetime(2013,9,1), 'm')
        self.assertTrue(result > 0.0)

        # day frequency makes no sense and should fail
        self.assertRaises(ValueError, prorate, datetime(2013,9,15), 'd')


class TestRangeFunctions(unittest.TestCase):
    def test_day_range(self):
        # length of day_range should equal integer argument
        self.assertEqual(len(day_range(30)), 30)

        # day range should give a 10 day index starting from 5/1/2013
        expected = pd.date_range(datetime(2013,5,1), datetime(2013,5,10))
        result = day_range(10, datetime(2013,5,1))
        self.assertTrue(result.equals(expected))

        # day range should give a 10 day index not including 5/1/2013
        expected = pd.date_range(datetime(2013,5,2), datetime(2013,5,11))
        result = day_range(10, datetime(2013,5,1), inclusive=False)
        self.assertTrue(result.equals(expected))

        # day range should work with negative integer argument
        expected = pd.date_range(datetime(2013,5,11), datetime(2013,5,20))
        result = day_range(-10, datetime(2013,5,20))
        self.assertTrue(result.equals(expected))

        # day range should not work with 0 days
        self.assertRaises(AssertionError, day_range, 0)












