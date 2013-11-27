import unittest
from unittest import mock

from datetime import datetime, date

import pandas as pd

from ..io.sql import read_frame, coerce_dtypes
from .utils import assert_series_equal, assert_frame_equal

class TestDataTypeCoercion(unittest.TestCase):

    def setUp(self):
        self.mapping = {
            'int': int,
            'float': float,
            'date': date,
            'datetime': datetime,
            'str': str
        }

        self.obj_frame = pd.DataFrame([(1,2.33,datetime(2013,6,1), date(2013,6,1), 'asdf')], 
                                      columns=['int','float','datetime','date', 'str'],
                                      dtype='O')

    def test_coerce_dtypes_uses_mapping(self):
        result = coerce_dtypes(self.obj_frame, self.mapping).dtypes.to_dict()
        expected = {
            'date': '<M8[ns]',
            'datetime': '<M8[ns]',
            'float': 'float64',
            'int': 'int32',
            'str': 'O'
        }

        self.assertEqual(result, expected)

    def test_coerce_dtypes_upcasts_int_to_float_on_nan(self):
        df = pd.DataFrame([(1,), (None,)], columns=['int'])

        result = coerce_dtypes(df, {'int': int}).dtypes.to_dict()
        expected = {'int': 'float64'}

        self.assertEqual(result, expected)

    def test_coerce_dtype_converts_date_to_timestamp(self):
        df = pd.DataFrame([(date(2010,1,3))], columns=['date'])

        result = coerce_dtypes(df, {'date': date}).dtypes.to_dict()
        expected = {'date': '<M8[ns]'}

        self.assertEqual(result, expected)


class TestReadFrame(unittest.TestCase):
    def setUp(self):
        pass

    def test_read_frame_returns_empty_frame(self):
        mock_conn = mock.Mock()
        mock_cursor = mock.Mock()
        mock_cursor.execute.return_value = None
        mock_cursor.fetchall.return_value = []
        mock_cursor.description = []
        mock_conn.cursor.return_value = mock_cursor

        df = read_frame('asdf', mock_conn)
        self.assertTrue(df.empty)

    def test_read_frame_returns_correct_column_names_and_dtypes(self):
        mock_conn = mock.Mock()
        mock_cursor = mock.Mock()
        mock_cursor.execute.return_value = None
        mock_cursor.fetchall.return_value = [(1,2.3)]
        mock_cursor.description = [('int', int), ('float', float)]
        mock_conn.cursor.return_value = mock_cursor

        result = read_frame('asdf', mock_conn)
        expected = pd.DataFrame([(1,2.3)], columns=['int', 'float'])

        assert_frame_equal(result, expected)

    def test_read_frame_is_called_with_parameters(self):
        mock_conn = mock.Mock()
        mock_cursor = mock.Mock()
        mock_cursor.execute.return_value = None
        mock_cursor.fetchall.return_value = []
        mock_cursor.description = []
        mock_conn.cursor.return_value = mock_cursor

        df = read_frame('select top 10', mock_conn, 'office')
        mock_cursor.execute.assert_called_with('select top 10', ['office'])

    def test_read_frame_is_called_without_parameters(self):
        mock_conn = mock.Mock()
        mock_cursor = mock.Mock()
        mock_cursor.execute.return_value = None
        mock_cursor.fetchall.return_value = []
        mock_cursor.description = []
        mock_conn.cursor.return_value = mock_cursor

        df = read_frame('select top 10', mock_conn)
        mock_cursor.execute.assert_called_with('select top 10')

    def test_read_frame_raises_on_duplicate_columns(self):
        mock_conn = mock.Mock()
        mock_cursor = mock.Mock()
        mock_cursor.execute.return_value = None
        mock_cursor.fetchall.return_value = []
        mock_cursor.description = [('A',),('A')]
        mock_conn.cursor.return_value = mock_cursor

        self.assertRaises(AssertionError, read_frame, 'select top 10', mock_conn)
