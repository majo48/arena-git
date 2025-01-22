"""
    Bounding Box for Copernicus data using the GLO-90 set of COG files:
      Info (height x width): 1 x 1 degrees latitude, longitude
      COG  (height x width): 1200 x 1200 elements
      Folder Naming Conventions:
        Copernicus_DSM_COG_[resolution]_[northing]_[easting]_00_DEM
          resolution: 30 (should be 90, but isn't)
          northing: N47_00
          easting:  E009_00
          Name: COPERNICUS_DSM_COG_30_N47_00_E009_DEM
            Bounding Box:
              top: 48.000
              bottom: 47.000
              left: 9.000
              right: 10.000
              The Foldername corresponds with the LL (lower left) of the contents
"""

import math

class BoundingBox:
    def __init__(self, north, south, west, east):
        """
            Valid for Western Europe & Asia only (ex. UK, Spain) 
        """
        # round parameters to multiples of one degree
        self.top = math.ceil(north)
        self.bottom = math.floor(south)
        self.left = math.floor(west)
        self.right = math.ceil(east)
        # other values
        self.tilenames = []
        self.unittests = []
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
                fldr = "Copernicus_DSM_COG_30_"+northing+"_"+easting+"_DEM"
                self.tilenames.append({
                    "top": row+1, "bottom": row, "left": col, "right": col+1, 
                    "fldr": fldr
                    })
                col += 1 # next up
            row += 1 # next right
        return

    def set_unittests(self, unittests):
        """
        Set the list of random unit tests 
        """
        self.unittests = unittests
        pass

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
        elif leading == 3:
            return "000"+rslt
        else:
            raise Exception('panic')
        

if __name__ == '__main__':
    print("This BoundigBox class module shall not be invoked on it's own.")

