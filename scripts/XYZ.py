"""
    XYZ with Copernicus elevation data.
    1200 x 1200 cells with geospatial coordinates and elevation data,
    the coordinates describe the centerpoint of the geospatial cell. 
"""

import os
import sys
import math

# define elevation matrix for COG-90 (accuracy: < 4 meters)
HIGH = 1200 # matrix height, equals cell size of 90 meters
WIDE = 1200 # matrix width, equals cell size of 90 meters
# number of digits after the decimal point in geospatial coordinates
DGTS = 6 # accuracy in cm is 5:111, 6:11, 7:1

class XYZ:
    def __init__(self, filename):
        pass

    def get_col_headers():
        pass

    def get_row_headers():
        pass

    def get_matrix():
        pass

    def get_test_log():
        pass



if __name__ == '__main__':
    print("This XYZ class module shall not be invoked on it's own.")