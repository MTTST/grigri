# -*- coding: utf-8 -*-
"""
    grigri.math
    ~~~~~~~~~~~~~~~~~~

    Miscellaneous math functions and formulas.
"""

from math import sqrt, sin, cos, atan2, pi

def euclidean_distance(x,y):
    """
    Returns the euclidean distance from the origin to a point in 2-D space.

    :param x: x-coordinate
    :param y: y-coordinate
    """

    return sqrt(x**2 + y**2)

def spherical_distance(lat1, lat2, long1, long2, in_miles=True):
    """ 
    Computes spherical distance between two coordinates on the surface of the
    earth. 

    :param lat1: Geographic latitude of the first coordinate.
    :param lat2: Geographic latitude of the second coordinate.
    :param long1: Geographic longitude of the first coordinate.
    :param long2: Geographic longitude of the second cocordinate.
    :param in_miles: If `True`, will return distance in miles; kilometers 
                     otherwise.
    """

    radius = 3956. if in_miles else 6371.  # radius of the earth 

    # radian conversion
    c = pi / 180.
    lat1 = lat1 * c
    lat2 = lat2 * c
    long1 = long1 * c
    long2 = long2 * c

    # apply the Haversine formula:
    # http://en.wikipedia.org/wiki/Haversine_formula
    # http://en.wikipedia.org/wiki/Great-circle_distance
    dlong = long2 - long1
    dlat = lat2 - lat1

    x = (pow(sin(dlat/2.0), 2) + cos(lat1) * cos(lat2) * 
         pow(sin(dlong/2.0), 2))
    angle = 2 * atan2(sqrt(x), sqrt(1-x))
    
    return radius * angle