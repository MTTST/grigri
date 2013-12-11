# -*- coding: utf-8 -*-
"""
    grigri.io.sql
    ~~~~~~~~~~~~~

    Methods that facilitate data retrieval and writing to a 
    SQL database.
"""

from datetime import datetime, date
import decimal

import numpy as np
import pandas as pd


def read_frame(sql, conn, params=None, coerce_default=True, coerce_ascii=False,
               squeeze=False):
    """
    Returns a DataFrame from the result set of a SQL statement.

    :param sql: SQL statement to execute
    :param conn: Valid database connection 
    :param params: List of parameters to feed into a parameterized query.
    :param coerce_default: Coerce columns to the default datatype specified in 
                           the metadata of the SQL table.
    :param coerce_ascii: Remove non-ascii charaters from string type columns.
    :param squeeze: Attempt to reduce DataFrame into a Series if possible.

    .. note ::
        The `pandas` library has its own `read_frame` function that you can 
        use. However, this function properly coerces columns to the correct
        data type, by inspecting the data type of the column in SQL.
    """

    cursor = conn.cursor()
    if params:
        if not isinstance(params, list):
            params = [params,]

        cursor.execute(sql, params)
    else:
        cursor.execute(sql)
    
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]

    # https://github.com/jephdo/grigri/issues/1
    assert len(list(columns)) == len(set(columns)), 'There are duplicate column names in the SQL statement.'

    cursor.close()
    conn.commit()

    result = pd.DataFrame.from_records(rows, columns=columns)

    if coerce_default:
        # mapping of column name -> column data type
        column_types = {col[0]: col[1] for col in cursor.description}
        result = coerce_dtypes(result, column_types)

    # TODO: not really sure the best way to encode ascii yet
    if coerce_ascii:
        pass
    
    return result

def coerce_dtypes(frame, columns):
    """
    Forces columns of a DataFrame to be the appropriate datatype. 
    The pandas DataFrame constructor sometimes doesn't infer the proper 
    data type, but we know the exact data type from the pyodbc cursor. 

    :param frame: DataFrame to possibly adjust datatypes for.
    :param columns: Dictionary of columns and the native Python type they 
                    should conform to.

    .. note ::
        Both date and datetime columns are converted to the native pandas 
        `timestamp` datatype
    .. warning :: 
        There are no native NaN's for boolean types, SQL NULL's will be converted
        to False.
    """

    for col, dtype in columns.items():
        if dtype in [datetime, date]:
            frame[col] = pd.to_datetime(frame[col])
        elif dtype is bool:
            frame[col] = np.bool_(frame[col])
        elif dtype is int:
            try:
                frame[col] = frame[col].astype(int)
            except ValueError:
                # there is no native integer type for NaN,
                # so if there are any NULL's in an integer 
                # column you have to cast to float:
                # http://pandas.pydata.org/pandas-docs/dev/gotchas.html#support-for-integer-na
                frame[col] = frame[col].astype(float)
        elif dtype in [float, decimal.Decimal]:
            frame[col] = frame[col].astype(float)

    return frame

def write_frame(frame, conn, table, clear_table=False):
    """ 
    Writes a DataFrame object to a SQL database table.

    :param frame: Target DataFrame to write to SQL
    :param conn: Database connection object to use.
    :param table: Name of SQL table to write to.
    :param clear_table: If `True`, will delete all rows in `table` before 
                        writing.

    .. warning ::
        Be careful which ODBC library you use when feeding in `conn`. It is 
        recommended that you use ceODBC for doing inserts to tables. 
        
        Previously we used the pyodbc library, but suffered huge write performance problems 
        because pyodbc wasn't correctly handling bulk inserts. See:
        http://stackoverflow.com/questions/5693885/pyodbc-very-slow-bulk-insert-speed

    """
    # assert isinstance(conn, ceODBC.Connection), 'Connection object must use the ceODBC module for writing'

    cursor = conn.cursor()
    try:
        if clear_table:
            cursor.execute('TRUNCATE TABLE [%s]' % table)

        safe_columns = ['[' + col.replace(' ','_').strip() + ']' 
                        for col in frame.columns]
        columns = ','.join(safe_columns)
        wildcards = ','.join(['?'] * len(safe_columns))

        insert_query = 'INSERT INTO %s (%s) VALUES (%s)' % (table, columns, wildcards)

        # Have to replace any kind of NaN types to None because SQL
        # only understands how to interpret None.
        data = []
        for x in frame.values:
            row = [None if pd.isnull(i) else i for i in x]
            cursor.execute(insert_query, row)

        # cursor.executemany(insert_query, data)
    except pyodbc.Error:
        raise
    else:
        cursor.close()
        conn.commit()