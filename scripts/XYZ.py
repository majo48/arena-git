"""
    XYZ with Copernicus elevation data.
    1200 x 1200 cells with geospatial coordinates and elevation data,
    the coordinates describe the centerpoint of the geospatial cell. 
"""

import os
import sys
import math
import logging

# define elevation matrix for COG-90 (accuracy: < 4 meters)
HIGH = 1200 # matrix height (cols), equals cell size of 90 meters
WIDE = 1200 # matrix width (rows), equals cell size of 90 meters
# number of digits after the decimal point in geospatial coordinates
DGTS = 6 # accuracy in cm is 5:111, 6:11, 7:1
# logging
LOGFILE = 'arena.log' # located in project repository (.ignored)

class XYZ:
    def __init__(self, filename):
        self.col_headers = [None]*WIDE
        self.row_headers = [None]*HIGH
        # create 2D matrix of integers organized in rows and cols
        self.matrix = [[None for i in range(WIDE)] for j in range(HIGH)]  
        # setup logging
        if os.path.exists(LOGFILE):
            os.remove(LOGFILE) # start a new logfile for each session
        logging.basicConfig(
            level=logging.DEBUG, 
            format='%(asctime)s %(levelname)s %(message)s',
            filename=LOGFILE,
            datefmt='%H:%M:%S'  
        ) 
        logging.debug('Start debugging session.')
        # convert text file to headers and matrix
        self.set_matrix(filename)

    def get_col_headers(self):
        if self.col_headers[0] is not None:
            return self.col_headers
        else:
            logging.warning('Column list is empty!')
            return [] 

    def get_row_headers(self):
        if self.row_headers[0] is not None:
            return self.row_headers
        else:
            logging.warning('Row list is empty!')
            return [] 

    def get_matrix(self):
        if self.matrix[0][0] is not None:
            return self.matrix
        else:
            logging.warning('Matrix lists are empty!')
            return [] 
    
    def set_matrix(self, filename):
        """
            read file and build matrix
        """
        pass


if __name__ == '__main__':
    print("This XYZ class module shall not be invoked on it's own.")