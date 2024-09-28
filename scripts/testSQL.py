#!/usr/bin/env python3

"""
    Test SQLite3 database
"""

from XYZ import XYZ
from SQL import SQL
import logging
import os

# variables =============================================
# number of digits after the decimal point in geospatial coordinates
DGTS = 6 # accuracy is 5:111cm, 6:11cm, 7:1cm
LOGFILE = 'arena.log' # located in project repository (.ignored)
XYZPATH = "/home/mart/arena-git/build/Copernicus_DSM_COG_30_N47_00_E009_00_DEM.txt"

# main code =============================================
# setup logging
if os.path.exists(LOGFILE):
    os.remove(LOGFILE) # start a new logfile for each session
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.FileHandler(LOGFILE)
    ]  
) 
logging.debug('Start new logging session.')

# convert text to database
with SQL(DGTS) as sqldb:
    xyz = XYZ(XYZPATH, sqldb)

# finish
logging.debug('Finished building database and logging session.')
