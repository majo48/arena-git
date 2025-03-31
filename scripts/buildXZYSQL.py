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

def clean_up_dir(path_to_folder):
    """
        Remove all local folders and files
    """
    for root, dirs, files in os.walk(path_to_folder):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))
    pass

def get_aws_tile(tilename):
    """
        Read Copernicus tile from AWS S3 using subprocess with aws (cli)
    """
    s3link = "s3://copernicus-dem-90m/"+tilename+"/"
    destination = config("TILE_FOLDER")+tilename+"/"
    if not os.path.isdir(destination):
        out = subprocess.run(["aws", "s3", "cp", s3link, destination, "--recursive"])
        print(out.stdout)
    return destination

def get_xyz_file(tilename):
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

def build_database(xdb, bb):
    """
        Build database following pattern:
            start at northwestern tile and pixel
                tiles: 1 degree x 1 degree
                pixels: 1200 x 1200 (approx 90 meters)
            tiles from left (west) to right (east), then
                  from top (north) to bottom (south)
    """
    previous_ll_bottom = None
    previous_ll_left = None
    for tile in bb.tiles:

        tilename = tile["fldr"]
        tile_bottom = tile["bottom"]
        tile_left = tile["left"]
        print("Tile:", tilename, "LL coordinate:", str((tile_bottom, tile_left)))

        # build tile
        aws_path = get_aws_tile(tilename)
        print("Downloaded from AWS to file: "+aws_path)

        # build XYZ file
        xyz_path = get_xyz_file(tilename)

        # build XYZ object
        xyz_obj = XYZ(xyz_path)

        # follow pattern and build database
        pixel_top = tile["pixel_top"]
        pixel_left = tile["pixel_left"]
        with Dbsql(xdb) as sqldb:
            # build database pattern: left(W) to right(E), and top(N) to bottom(S)
            if (previous_ll_bottom is None) and (previous_ll_left is None):
                # use case: empty database
                sqldb.set_row_headers(xyz_obj.row_headers)
                sqldb.set_col_headers(xyz_obj.col_headers)
                sqldb.set_rows(xyz_obj.matrix, pixel_top, pixel_left, bb.max_bytes_in_row)
            elif (tile_bottom == previous_ll_bottom) and (tile_left == previous_ll_left + 1):
                # use case: one tile to the right
                sqldb.add_col_headers(xyz_obj.col_headers)
                sqldb.add_rows(xyz_obj.matrix, pixel_top, pixel_left, bb.max_bytes_in_row)
                # note: rows_offset does not change
            elif tile_bottom == previous_ll_bottom - 1:
                # use case: first tile below (new tile row)
                sqldb.add_row_headers(xyz_obj.row_headers)
                sqldb.set_rows(xyz_obj.matrix, pixel_top, pixel_left, bb.max_bytes_in_row)
            else:
                # undefined state, sequence, pattern
                raise AssertionError("Lower Left (LL) does not follow proper pattern: W to E, N to S.")
            # end if
            sqldb.set_metadata_item(xyz_path, xyz_obj.bounding_box)
        # end with
        previous_ll_bottom = tile_bottom
        previous_ll_left = tile_left
    pass  # end for
    print("Finished building database (success).")

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
bounding_box = BoundingBox(
    north=float(config("ARENA_NORTH")),
    south=float(config("ARENA_SOUTH")),
    west=float(config("ARENA_WEST")),
    east=float(config("ARENA_EAST"))
)
print("Bounding Box:", bounding_box.top, bounding_box.bottom, bounding_box.left, bounding_box.right)
print("Tiles:", str(bounding_box.number_of_tiles))

# build ====
build_database(xdb_path, bounding_box)
exit(0)
