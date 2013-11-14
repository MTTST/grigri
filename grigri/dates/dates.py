from datetime import datetime

def strip_time(dt):
    """
    Returns datetime object stripped of time information.

    >>> strip_time(datetime(2013, 9, 5, 17, 1, 52, 661000))
    datetime.datetime(2013, 9, 5, 0, 0)
    """

    return datetime(dt.year, dt.month, dt.day)
