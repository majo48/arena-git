#!/usr/bin/env python3

"""
    Build XYZ file from Copernicus data residing on AWS S3 &
    Build SQLite3 database using XYZ file data
        Database file is in config("TILE_FOLDER"), filename 'arena.db'
"""

# packages ========

from BoundingBox import BoundingBox 
from XYZ import XYZ
import subprocess
import os
import shutil
import logging
from decouple import config
from scripts.Dbsql import Dbsql

# functions ========

def clean_up_dir(pathtofolder):
    """
        Remove all local folders and files
    """
    for root, dirs, files in os.walk(pathtofolder):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))
    pass

def get_AWS_tile(tilename):
    """
        Read Copernicus tile from AWS S3 using subprocess with aws (cli)
    """
    s3link = "s3://copernicus-dem-90m/"+tilename+"/"
    destination = config("TILE_FOLDER")+tilename+"/"
    if not os.path.isdir(destination):
        out = subprocess.run(["aws", "s3", "cp", s3link, destination, "--recursive"])
        print(out.stdout)
    return destination

def get_XYZ_file(tilename):
    """
        Read Copernicus tile and convert to XYZ format using subprocess with GDAL (cli)
    """
    tile_folder = config("TILE_FOLDER")
    source = tile_folder+tilename+"/"+tilename+".tif"
    destination = tile_folder+tilename+".txt"
    if not os.path.exists(destination):
        out = subprocess.run(["gdal_translate", "-of", "XYZ", source, destination])
        print(out.stdout)
    return destination

# main code ==============================================

# remove existing folders and files
clean_up_dir(config("TILE_FOLDER"))
logfile = config("LOG_FILENAME")
if os.path.exists(logfile):
    os.remove(logfile) # if it exists
xdb_path = config("DB_FILENAME")
if os.path.exists(xdb_path):
    os.remove(xdb_path) # if it exists

# setup logging ====
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    handlers=[logging.FileHandler(logfile)])
logging.debug('Start new logging session.')

# set the bounding box for the operating area, all values rounded to one degree
bb = BoundingBox(
    north=float(config("ARENA_NORTH")),
    south=float(config("ARENA_SOUTH")),
    west=float(config("ARENA_WEST")),
    east=float(config("ARENA_EAST"))
)
print("Bounding Box:", bb.top, bb.bottom, bb.left, bb.right)
print("Tiles:", str(bb.number_of_tiles))

# start building
for name in bb.tilenames:
    
    # build tile
    tilename = name["fldr"]
    print("Tile:", tilename)
    aws_path = get_AWS_tile(tilename)
    
    # build XYZ file
    xyz_path = get_XYZ_file(tilename)

    with Dbsql(xdb_path) as sqldb:
        # build XYZ object
        xyz_obj = XYZ(xyz_path)
        # build database
        sqldb.set_row_headers(xyz_obj.row_headers)
        sqldb.set_col_headers(xyz_obj.col_headers)
        sqldb.set_rows(xyz_obj.matrix, xyz_path, xyz_obj.bounding_box)
        sqldb.set_metadata(xyz_path, xyz_obj.bounding_box)
    pass # end for
print("Finished building database.")
exit(0)
