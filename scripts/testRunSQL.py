#!/usr/bin/env python3

"""
    Test run script, exercising the SQLite3 database
"""

from Dbsql import Dbsql
from Route import Route
from Dbcache import Dbcache
import json
import logging
from decouple import config

# constants ========

# locations (lat, long)
cityZug = (47.170358, 8.518013)         # (lat, long)
cityBaar = (47.19455, 8.52646)          # (lat, long)
cityCham = (47.18124, 8.45908)          # (lat, long)
citySins = (47.19112, 8.39574)          # (lat, long)
cityBremgarten = (47.35040, 8.31802)    # (lat, long)
cityWohlen = (47.36173, 8.21417)        # (lat, long)
citySeon = (47.34673, 8.16113)          # (lat, long)

# main ========
try:
    logging.debug('Begin unit test for database.')
    with Dbcache(config("DB_FILENAME")) as dbcache:
        #
        # create test route, waypoints and tracks
        metadata = dbcache.dbsql.get_arena_bounding_box()
        route = Route(metadata)
        waypoints = [ cityZug, cityBaar, cityCham ]
        tracks = route.build_route('Zug-Baar-Cham', waypoints)
        #
        # test database elevation profile
        print("Meters above sea level:")
        for track in tracks["tracks"]:
            elevation = dbcache.get_flight_information( track[0], track[1])
            # print current coordinates, (cell elevation, next cell elevation, heading, compass)
            print(  f'{track[0]:.6f}'+', '+f'{track[1]:.6f}'+', '+str(elevation))
        pass
    logging.debug('End unit test for database.')
    exit(0)
except Exception as err:
    logging.error("Test route, unknown error: " + err.args)
    exit(1)
