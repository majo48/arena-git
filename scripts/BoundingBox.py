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
              The folder name corresponds with the LL (lower left) of the contents
"""

# packages ========

import math

# constants ========

DEM_TILE_PIXELS = 1200 # one GLO-90 tile has 1200 x 1200 pixels (per 1 x 1 degrees)
SIZE_FACTOR = 2.4

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
        self.pixels = DEM_TILE_PIXELS
        self.tiles = []
        self.unittests = []
        self.number_of_tiles = (self.top-self.bottom)*(self.right-self.left)
        self.north_south_pixels = (self.top - self.bottom) * DEM_TILE_PIXELS
        self.east_west_pixels = (self.right - self.left) * DEM_TILE_PIXELS
        self.max_bytes_in_row = SIZE_FACTOR * self.east_west_pixels
        self.set_tiles()
        pass

    def set_tiles(self):
        """
            derive 'tile names' and 'tile bounding boxes' from BoundingBox
            parameters north, south, west, east:
                one file (tile) per 1 x 1 degree
                ordered from left (west) to right (east) and
                ordered from top (north) to bottom (south)
        """
        row = self.top-1
        col = self.left
        pixel_top = 0
        while row >= self.bottom:
            pixel_left = 0
            while col < self.right:
                northing = "N"+self.leading_zeros(row, 2)+"_00"
                easting = "E"+self.leading_zeros(col, 3)+"_00"
                fldr = "Copernicus_DSM_COG_30_"+northing+"_"+easting+"_DEM"
                self.tiles.append({
                    "top": row+1, "bottom": row, "left": col, "right": col+1,
                    "pixel_left": pixel_left, "pixel_top": pixel_top,
                    "fldr": fldr
                    })
                col += 1 # next right
                pixel_left += DEM_TILE_PIXELS
            row -= 1 # next down
            col = self.left # reset column
            pixel_top += DEM_TILE_PIXELS
        return

    def set_unittests(self, unittests):
        """
        Set the list of random unit tests 
        """
        self.unittests = unittests
        pass

    @staticmethod
    def leading_zeros(integer_value, digits):
        """
            Convert integer value to string and, if needed, add leading zeros
        """
        rslt = str(integer_value)
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
    print("This BoundingBox class module shall not be invoked on it's own.")

