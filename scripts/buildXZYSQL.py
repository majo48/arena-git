#!/usr/bin/env python3

"""
    Build XYZ file from Copernicus data residing on AWS S3, and
    build SQLite3 database using XYZ file data
"""

# packages ========

from BoundingBox import BoundingBox 
from XYZ import XYZ
import subprocess
import os
import shutil
import logging
from decouple import config

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

def get_tile(tilename):
    """
        Read Copernicus tile from AWS S3 using subprocess with aws (cli)
    """
    s3link = "s3://copernicus-dem-90m/"+tilename+"/"
    destination = config("TILE_FOLDER")+tilename+"/"
    if not os.path.isdir(destination):
        out = subprocess.run(["aws", "s3", "cp", s3link, destination, "--recursive"])
        print(out.stdout)
    pass

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
    pass
    return destination

# main code ==============================================

# remove existing folders and files
clean_up_dir(config("TILE_FOLDER"))
logfile = config("LOG_FILENAME")
if os.path.exists(logfile):
    os.remove(logfile) # if it exists
xdbpath = config("DB_FILENAME")
if os.path.exists(xdbpath):
    os.remove(xdbpath) # if it exists

# setup logging ====
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    handlers=[logging.FileHandler(logfile)])
logging.debug('Start new logging session.')

# set the bounding box for the operating area, all values will be rounded to one degree
bb = BoundingBox(
    north=config("ARENA_NORTH"),
    south=config("ARENA_SOUTH"),
    west=config("ARENA_WEST"),
    east=config("ARENA_EAST")
)
print("Bounding Box:", bb.top, bb.bottom, bb.left, bb.right)
print("Tiles:", str(bb.number_of_tiles))

# start building
for name in bb.tilenames:
    
    # build tile
    tilename = name["fldr"]
    print("Tile:", tilename)
    get_tile(tilename)
    
    # build XYZ file and object
    source = get_XYZ_file(tilename)
    xyz = XYZ(source)
    
    # build database
    pass # work in progress
pass
