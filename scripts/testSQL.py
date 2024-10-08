#!/usr/bin/env python3

"""
    Test SQLite3 database
"""

from XYZ import XYZ
from SQL import SQL
import logging
import os
import sys

# constants =============================================
# number of digits after the decimal point in geospatial coordinates
DGTS = 6 # accuracy depends on DGTS { 5: 111cm, 6: 11cm, 7: 1cm}
# filenames and paths
LOGFILE = '/home/mart/arena-git/build/arena.log' # normally .ignored
XYZPATH = "/home/mart/arena-git/build/Copernicus_DSM_COG_30_N47_00_E009_00_DEM.txt"
XDBPATH = "/home/mart/arena-git/build/arena.db"

def calculate_size(obj):
    """
    Calculate the real size of standard Python objects 
    the calculation does not consider shared objects
    the value is the objects maximal size in bytes
    """
    size = sys.getsizeof(obj)
    if isinstance(obj, dict):
        size += sum(calculate_size(v) for v in obj.values())
        size += sum(calculate_size(k) for k in obj.keys())
    elif isinstance(obj, (list, tuple, set)):
        size += sum(calculate_size(v) for v in obj)
    elif isinstance(obj, bytes):
        size += len(obj)
    elif isinstance(obj, str):
        size += len(obj.encode('utf-8'))
    elif isinstance(obj, type(None)):
        size += 0
    elif isinstance(obj, (int, float)):
        size += sys.getsizeof(obj)
    else:
        size += sum(
            calculate_size(getattr(obj, attr))
            for attr in dir(obj)
            if not callable(getattr(obj, attr)) and not attr.startswith("__")
        )

    return size

# main code =============================================

# setup logging ====
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

# convert text to database ====
with SQL(XDBPATH) as sqldb:
    xyz = XYZ(XYZPATH)
    logging.debug('Finished building XYZ.')
    sqldb.set_row_headers(xyz.row_headers)
    sqldb.set_col_headers(xyz.col_headers)
    sqldb.set_matrix(xyz.matrix, XYZPATH, xyz.bounding_box)
pass
logging.debug('row headers: '+str(calculate_size(xyz.row_headers)))
logging.debug('col headers: '+str(calculate_size(xyz.col_headers)))
logging.debug('matrix: '+str(calculate_size(xyz.matrix)))

# finish ====
logging.debug('Finished building database and logging session.')
