#!/usr/bin/env python3

"""
    Test GDAL: gdallocationinfo
"""

import os
import sys
import subprocess

# tiles
destination_tiles = "/home/mart/arena-git/build/tiles/"
tilename = "Copernicus_DSM_COG_30_N47_00_E008_00_DEM/Copernicus_DSM_COG_30_N47_00_E008_00_DEM.tif"
# locations (lat, long)
cityZug = (47.170358, 8.518013)         # (lat, long)
cityBaar = (47.19455, 8.52646)          # (lat, long)

def get_elevation_gdal(lat, long):
    """
        Read Copernicus tile and convert lat, long to elevation (in meters)
    """
    source = destination_tiles+tilename
    if os.path.exists(source):
        out = subprocess.run(["gdallocationinfo", "-xml", "-wgs84", source, str(long), str(lat)])
        print(out.stdout)
    else:
        print('Filename does not exist: '+source)
    return out

# main

elevation = get_elevation_gdal( cityZug[1], cityZug[0] )
"""
Returns: 
<Report pixel="47004" line="47378">
  <Alert>Location is off this file! No further details to report.</Alert>
</Report>
None
"""

print('work in progress')
