#!/usr/bin/env python3

"""
    Test OSGEO: GDAL
"""

import os
import sys
from osgeo import gdal # ERROR: ModuleNotFoundError: No module named 'osgeo'

# tiles
destination_tiles = "/home/mart/arena-git/build/tiles/"
tilename = "Copernicus_DSM_COG_30_N47_00_E008_00_DEM/Copernicus_DSM_COG_30_N47_00_E008_00_DEM.tif"
# locations (lat, long)
cityZug = (47.170358, 8.518013)         # (lat, long)
cityBaar = (47.19455, 8.52646)          # (lat, long)

# main

gdal.UseExceptions()

ds = gdal.Open(destination_tiles+tilename)
band = ds.GetRasterBand(1)
elevation = band.ReadAsArray()

print(elevation.shape)
pass