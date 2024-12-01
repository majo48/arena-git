#!/usr/bin/env python3

"""
    Calculating the compass direction between two points in Python
"""

import math

def direction_lookup(destination_x, origin_x, destination_y, origin_y):
    """
    Reference: www.analytics-link.com. Andrew Jones, Aug 21, 2018
    """
    deltaX = destination_x - origin_x # longitude
    deltaY = destination_y - origin_y # latitude
    degrees_temp = math.atan2(deltaX, deltaY)/math.pi*180
    if degrees_temp < 0:
        degrees_final = 360 + degrees_temp
    else:
        degrees_final = degrees_temp
    compass_brackets = ["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"]
    compass_lookup = round(degrees_final / 45)
    return compass_brackets[compass_lookup], degrees_final


def directions(fromPlace: tuple, toPlace: tuple):
    """
    Give the directions going fromPlace (lat, long) toPlace (lat, long)
    """
    deltaX = toPlace[1] - fromPlace[1] # longitude
    deltaY = toPlace[0] - fromPlace[0] # latitude
    degrees_temp = math.atan2(deltaX, deltaY)/math.pi*180
    if degrees_temp < 0:
        degrees_final = 360 + degrees_temp
    else:
        degrees_final = degrees_temp
    compass_brackets = ["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"]
    compass_lookup = round(degrees_final / 45)
    return compass_brackets[compass_lookup], degrees_final
 

print( direction_lookup(7,2,7,3)) # ('NE', 51.340191745909905)

print( directions( (3,2), (7,7) ))