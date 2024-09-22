#!/usr/bin/env python3

"""
    Read Copernicus tile, convert to XYX text format
"""

import os
import sys
import subprocess

tile_path_filename = "/mnt/d/myprojects/vps-git/cmd/getCOGdata/tile1/Copernicus_DSM_COG_30_N47_00_E008_00_DEM.tif"
tile_output = "/home/mart/arena-git/build/tile1.txt"

def main():
    """
        use cli converter in order to avoid any python bindings to gdal (tricky IMHO)
    """
    print('Read Copernicus Tile and convert to XYZ text file.')
    out = subprocess.run(["gdal_translate", "-of", "XYZ", tile_path_filename, tile_output])
    print(out.stdout)

if __name__ == '__main__':
    sys.exit(main())
