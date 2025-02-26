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

logging.debug('Begin unit test for database.')
with Dbcache(config("DB_FILENAME")) as dbcache:
    #
    # create test route, waypoints and tracks
    metadata = dbcache.dbsql.get_metadata()
    route = Route(json.loads(metadata[1]))
    waypoints = [ cityZug, cityBaar, cityCham ]
    tracks = route.build_route('Zug-Baar-Cham', waypoints)
    #
    # test database elevation profile
    print("Meters above sea level:")
    for track in tracks["tracks"]:
        # masl = cache.get_elevation(track[0], track[1]) # lat, long
        # print(  'track: ('+f'{track[0]:.6f}'+', '+f'{track[1]:.6f}'+', elevation: '+str(masl)+')')
        elevation = dbcache.get_flight_information( track[0], track[1])
        print(  f'{track[0]:.6f}'+', '+f'{track[1]:.6f}'+', '+str(elevation))
    pass
logging.debug('End unit test for database.')
