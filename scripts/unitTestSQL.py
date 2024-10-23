#!/usr/bin/env python3

"""
    Unit test SQLite3 database
"""

from SQL import SQL
from Route import Route
import json
import logging
import math
import os
import sys

# constants ========

# filenames and paths
# XDBPATH = "/home/mart/arena-git/build/arena.db" # in WSL Project
XDBPATH = "/mnt/c/Users/mart/Desktop/arena.db" # in Windows, Debug with DB Browser App

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
with SQL(XDBPATH) as sqldb:
    metadata = sqldb.get_metadata()
    route = Route(json.loads(metadata[1]))
    waypoints = [ cityZug, cityBaar, cityCham ]
    tracks = route.build_route('Zug-Baar-Cham', waypoints)
    prvsTrack = None
    for track in tracks["tracks"]:
        if prvsTrack == None:
            print('track: '+str(track))
        else:
            dstnc = int(route.calc_distance(prvsTrack, track))
            print('track: '+str(track)+', distance: '+str(dstnc))            
        prvsTrack = track
    pass
logging.debug('End unit test for database.')
