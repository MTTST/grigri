# -*- coding: utf-8 -*-
"""
    grigri.transforms
    ~~~~~~~~~~~~~~~~~~

    Functions that transform Series and DataFrames.
"""

import pandas as pd

def squeeze(frame):
    """
    """

    # trivial case: squeeze cannot make a Series
    # any smaller
    if isinstance(frame, pd.Series):
        return frame

    num_columns = len(frame.columns)

    # single column DataFrame -> select out only column
    if num_columns == 1:
        return frame.ix[:,0]

    if num_columns == 2:
        pass
        # first detect any datetime cols




    # first try squeezing single column dataframes into series
    if hasattr(data, 'columns') and len(data.columns) == 1:
        col = data.columns[0]
        data = data[col]
        data.name = col
        
    # lastly just return old data
    return data