#!/usr/bin/env python3

"""
    BuiUnit test SQLite3 database
"""

from SQL import SQL
import json
import math
import os
import sys

# constants ========

# filenames and paths
# XDBPATH = "/home/mart/arena-git/build/arena.db" # in WSL Project
XDBPATH = "/mnt/c/Users/mart/Desktop/arena.db" # in Windows, Debug with DB Browser App

# locations (lat, long)
cityZug = (47.170358, 8.518013)         # (lat, long)
cityBremgarten = (47.35040, 8.31802)    # (lat, long)
cityWohlen = (47.36173, 8.21417)        # (lat, long)
citySeon = (47.34673, 8.16113)          # (lat, long)

def inScope(boundingBox, city: tuple):
    """
    check if city tuple is inside the scope of the bounding box
        True:   OK, inside bounding box
        False:  outside of scope 
    """
    return False # work in progress

def buildRoute(fromCity: tuple, toCity: tuple, steps: int):
    """
    build a route from one city, to another city, in 'steps'
    defined by a (lat, long) tuple
    """
    route = [None]*steps # mutable
    route[0] = fromCity
    route[steps-1] = toCity
    latDelta = (toCity[0]-fromCity[0])/(steps-1)
    lngDelta = (toCity[1]-fromCity[1])/(steps-1)
    for i in range(1, steps-1):
        prvs = route[i-1]
        lat = prvs[0]+latDelta
        lng = prvs[1]+lngDelta
        route[i] = (lat, lng)
    return route


# main ========

with SQL(XDBPATH) as sqldb:
    col_headers = sqldb.get_col_headers()
    row_headers = sqldb.get_row_headers()
    metadata = sqldb.get_metadata()
    bb = json.loads(metadata[1])
    if inScope(bb, cityZug) and inScope(bb, cityBremgarten):
        waypoints = buildRoute(cityZug, cityBremgarten, 10)
        prvs = None
        for waypoint in waypoints:
            if prvs == None:
                print("Waypoint: "+str(waypoint))
                prvs = waypoint
            else:
                delta = math.sqrt((waypoint[0]-prvs[0])**2 + (waypoint[1]-prvs[1])**2)
                print("Waypoint: "+str(waypoint)+", Delta: "+str(delta))
                prvs = waypoint
        pass
    else:
        print("Waypoints aka. route is out of scope aka. outside of Bounding Box!")
    pass
pass
