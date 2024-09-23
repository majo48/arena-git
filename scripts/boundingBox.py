#!/usr/bin/env python3

"""
    Bounding Box for Copernicus data using the GLO-90 set of COG files:
      Info (height x width): 1 x 1 degrees latitude, longitude
      COG  (height x width): 1200 x 1200 elements
      Folder Naming Conventions:
        Copernicus_DSM_COG_[resolution]_[northing]_[easting]_DEM
          resolution: 90
          northing: N47_00
          easting:  E009_00
          Name: COPERNICUS_DSM_COG_N47_00_E009_DEM
            Bounding Box:
              top: 48.000
              bottom: 47.000
              left: 9.000
              right: 10.000
              The Foldername corresponds with the LL (lower left) of the contents
"""

import math

class BoundingBox:
    def __init__(self, top, bottom, left, right):
        """
            Valid for Western Europe & Asia only (ex. UK, Spain) 
        """
        self.top = math.ceil(top)
        self.bottom = math.floor(bottom)
        self.left = math.floor(left)
        self.right = math.ceil(right)
        self.names = []
        self.number_of_tiles = (self.top-self.bottom)*(self.right-self.left)
        self.set_names()

    def set_names(self):
        """
            derive names from bounding box, one file per 1 x 1 degree  
        """
        row = self.bottom
        col = self.left
        while row < self.top:
            while col < self.right:
                northing = "N"+self.leading_zeros(row, 2)+"_00"
                easting = "E"+self.leading_zeros(col, 3)+"_00"
                fldr = "Copernicus_DSM_COG_90_"+northing+"_"+easting+"_DEM"
                self.names.append({
                    "top": row+1, "bottom": row, "left": col, "right": col+1, 
                    "fldr": fldr
                    })
                col += 1 # next up
            row += 1 # next right
        return

    def leading_zeros(self, iVal, digits):
        """
            Convert integer value to string and, if needed, add leading zeros
        """
        rslt = str(iVal)
        leading = digits - len(rslt)
        if leading == 0:
            return rslt
        elif leading == 1:
            return "0"+rslt
        elif leading == 2:
            return "00"+rslt
        elif leading == 2:
            return "000"+rslt
        else:
            raise Exception('panic')
        

bb = BoundingBox(48.000, 47.000, 9.000, 10.000)
print(bb.top, bb.bottom, bb.left, bb.right)
for name in bb.names:
    print(name["fldr"])

