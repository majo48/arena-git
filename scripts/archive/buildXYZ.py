#!/usr/bin/env python3

"""
    Build XYZ file from Copernicus data residing on AWS S3
"""

from BoundingBox import BoundingBox 
from XYZ import XYZ
import subprocess
import os
from decouple import config

def get_tile(tilename):
    """
        Read Copernicus tile from AWS S3 using aws (cli)
    """
    s3link = "s3://copernicus-dem-90m/"+tilename+"/"
    destination_tiles = config("TILE_FOLDER")
    destination = destination_tiles+tilename+"/"
    if not os.path.isdir(destination):
        out = subprocess.run(["aws", "s3", "cp", s3link, destination, "--recursive"])
        print(out.stdout)
    pass

def get_XYZ(tilename):
    """
        Read Copernicus tile and convert to XYZ format using GDAL (cli)
        Reference: gdal_translate --format XYZ
    """
    destination_tiles = config("TILE_FOLDER")
    source = destination_tiles+tilename+"/"+tilename+".tif"
    destination = destination_tiles+tilename+".txt"
    if not os.path.exists(destination):
        out = subprocess.run(["gdal_translate", "-of", "XYZ", source, destination])
        print(out.stdout)
    pass

def check_XYZ(tilename):
    """
        Check XYZ file for any inconsistencies
    """
    destination_tiles = config("TILE_FOLDER")
    source = destination_tiles+tilename+".txt"
    # continue here

# main code ==============================================
# one name
bb = BoundingBox(48.000, 47.000, 8.000, 9.000) 
# two tiles
# bb = BoundingBox(48.000, 47.000, 8.000, 10.000) 
# swiss tiles
# bb = BoundingBox(47.828, 45.737, 5.823, 10.684) 

print("Bounding Box:", bb.top, bb.bottom, bb.left, bb.right)
print("Tiles:", str(bb.number_of_tiles))
for name in bb.tilenames:
    tilename = name["fldr"]
    print("Tile:", tilename)
    get_tile(tilename)
    get_XYZ(tilename)
    check_XYZ(tilename)
pass
