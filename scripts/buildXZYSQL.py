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

# local folders for storing tiles and XYZ files ========

DESTINATION_TILES = "/home/mart/arena-git/build/tiles/"
DESTINATION_XYZ = "/home/mart/arena-git/build/"
LOGFILE = '/home/mart/arena-git/build/arena.log' # normally .ignored
XDBPATH = "/mnt/c/Users/mart/Desktop/arena.db"   # in Windows, Debug with DB Browser App

# geo coordinates of the operating area ========
NORTH = 48.000
SOUTH = 47.000
WEST  = 8.000
EAST  = 10.000

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
    destination = DESTINATION_TILES+tilename+"/"
    if not os.path.isdir(destination):
        out = subprocess.run(["aws", "s3", "cp", s3link, destination, "--recursive"])
        print(out.stdout)
    pass

def get_XYZ_file(tilename):
    """
        Read Copernicus tile and convert to XYZ format using subprocess with GDAL (cli)
    """
    source = DESTINATION_TILES+tilename+"/"+tilename+".tif"
    destination = DESTINATION_XYZ+tilename+".txt"
    if not os.path.exists(destination):
        out = subprocess.run(["gdal_translate", "-of", "XYZ", source, destination])
        print(out.stdout)
    pass


# main code ==============================================

# remove existing folders and files
clean_up_dir(DESTINATION_TILES)
clean_up_dir(DESTINATION_XYZ)
if os.path.exists(LOGFILE): 
    os.remove(LOGFILE) # if it exists
if os.path.exists(XDBPATH): 
    os.remove(XDBPATH) # if it exists

# setup logging ====
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    handlers=[logging.FileHandler(LOGFILE)]) 
logging.debug('Start new logging session.')

# set the bounding box for the operating area, all values will be rounded to one degree
bb = BoundingBox(north=NORTH, south=SOUTH, west=WEST, east=EAST) 
print("Bounding Box:", bb.top, bb.bottom, bb.left, bb.right)
print("Tiles:", str(bb.number_of_tiles))

# start building
for name in bb.tilenames:
    
    # build tile
    tilename = name["fldr"]
    print("Tile:", tilename)
    get_tile(tilename)
    
    # build XYZ file and object
    get_XYZ_file(tilename)
    source = DESTINATION_XYZ+tilename+".txt"
    xyz = XYZ(source)
    
    # build database
    pass # work in progress
pass
