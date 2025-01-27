#!/usr/bin/env python3

"""
    Build SQLite3 database using XYZ file data
"""

from XYZ import XYZ
from scripts.Dbsql import Dbsql
import logging
import os
import sys
from decouple import config

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
logfile = config("LOG_FILENAME")
if os.path.exists(logfile):
    os.remove(logfile) # start a new logfile for each session
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.FileHandler(logfile)
    ]  
) 
logging.debug('Start new logging session.')

# convert text to database ====
xdbpath = config("DB_FILENAME")
with Dbsql(xdbpath) as sqldb:
    xyzpath = config("XYZ_FILENAME")
    xyz = XYZ(xyzpath)
    logging.debug('Finished building XYZ object.')
    sqldb.set_row_headers(xyz.row_headers)
    sqldb.set_col_headers(xyz.col_headers)
    sqldb.set_rows(xyz.matrix, xyzpath, xyz.bounding_box)
    sqldb.set_metadata(xyzpath, xyz.bounding_box)
    logging.debug("Finished building database.")
pass
logging.debug('row headers: '+str(calculate_size(xyz.row_headers))+' bytes.')
logging.debug('col headers: '+str(calculate_size(xyz.col_headers))+' bytes.')
logging.debug('matrix: '+str(calculate_size(xyz.matrix))+' bytes.')

# finish ====
logging.debug('Finished logging session.')
