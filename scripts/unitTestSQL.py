#!/usr/bin/env python3

"""
    Unit test script, exercising the SQLite3 database
"""

from SQL import SQL
from Route import Route
import json
import logging

# constants ========

# filenames and paths
# XDBPATH = "/home/mart/arena-git/build/arena.db" # in WSL Project
XDBPATH = "/mnt/c/Users/mart/Desktop/arena.db" # in Windows, Debug with 'DB Browser' App

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
    #
    # create test route, waypoints and tracks
    metadata = sqldb.get_metadata()
    route = Route(json.loads(metadata[1]))
    waypoints = [ cityZug, cityBaar, cityCham ]
    tracks = route.build_route('Zug-Baar-Cham', waypoints)
    #
    # test equidistant tracks
    print("Track-point information:")
    prvsTrack = None
    for track in tracks["tracks"]:
        sTrack = '('+f'{track[0]:.6f}'+', '+f'{track[1]:.6f}'+')'
        if prvsTrack == None:
            print('track: '+sTrack+', 1st waypoint')
        else:
            dstnc = int(route.calc_distance(prvsTrack, track))
            print('track: '+sTrack+', distance: '+str(dstnc))            
        prvsTrack = track
    #
    # test database elevation profile
    print("Meters above sea level:")
    for track in tracks["tracks"]:
        masl = sqldb.get_nearest_neighbor(track[0], track[1])
        print(  'track: ('+f'{track[0]:.6f}'+', '+f'{track[1]:.6f}'+', elevation: '+str(masl)+')')
        # masl = sqldb.get_weighted_elevation(track[0], track[1])
        # print( f'{track[0]:.6f}'+', '+f'{track[1]:.6f}'+', '+ str(masl) )
    pass
logging.debug('End unit test for database.')
