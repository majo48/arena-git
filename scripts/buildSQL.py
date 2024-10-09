#!/usr/bin/env python3

"""
    Build SQLite3 database
"""

from XYZ import XYZ
from SQL import SQL
import logging
import os
import sys

# constants =============================================
# filenames and paths
LOGFILE = '/home/mart/arena-git/build/arena.log' # normally .ignored
XYZPATH = "/home/mart/arena-git/build/Copernicus_DSM_COG_30_N47_00_E009_00_DEM.txt"
# XDBPATH = "/home/mart/arena-git/build/arena.db" # in WSL Project
XDBPATH = "/mnt/c/Users/mart/Desktop/arena.db" # in Windows, Debug with DB Browser App
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
    print("Building database, please wait ...")
    sqldb.set_row_headers(xyz.row_headers)
    logging.debug('Built row headers.')
    sqldb.set_col_headers(xyz.col_headers)
    logging.debug('Built column headers.')
    sqldb.set_matrix(xyz.matrix, XYZPATH, xyz.bounding_box)
    logging.debug('Built matrix rows.')
pass
logging.debug('row headers: '+str(calculate_size(xyz.row_headers))+' bytes.')
logging.debug('col headers: '+str(calculate_size(xyz.col_headers))+' bytes.')
logging.debug('matrix: '+str(calculate_size(xyz.matrix))+' bytes.')

# finish ====
logging.debug('Finished building database and logging session.')
