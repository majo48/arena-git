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
EDGE = 1200 # matrix height (cols) and width (rows), equals cell size of 90 x 90 meters
# number of digits after the decimal point in geospatial coordinates
DGTS = 6 # accuracy is 5:111cm, 6:11cm, 7:1cm
# logging
LOGFILE = 'arena.log' # located in project repository (.ignored)

class XYZ:
    def __init__(self, filename):
        self.col_headers = [None]*EDGE
        self.row_headers = [None]*EDGE
        # create 2D matrix of integers organized in rows and cols
        self.matrix = [[None for i in range(EDGE)] for j in range(EDGE)]  
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
            line: three numbers, sepatated with spaces
                longitude (9.xxx) in degrees east of Greenwich (G: Laengegrad)
                latitude (48.xxx) in degrees north of equator (G: Breitengrad)
                elevation (714.xxx) in meters above sea level
        """
        try:
            file = open(filename, "r")
            for row in range(EDGE):
                for col in range(EDGE):
                    line = file.readline()
                    if not line:
                        raise ValueError("Error in set_matrix: premature end of file.")
                    self.set_cell(row, col, line)
                pass
            pass
            file.close()
        except ValueError as err:
            logging.error(err.args)

    def set_cell(self, row, col, line):
        """
            convert line to XYZ cell item
        """
        try:
            # build cell, XYZ ====
            li = line.split(" ")
            fctr = 10 ** DGTS
            x = int(float(li[0])*fctr)  # col index converted to int * 1000000
            y = int(float(li[1])*fctr)  # row index converted to int * 1000000
            z = int(float(li[2])) # elevation converted to int meters
            # build col headers ====
            if row == 0:
                self.col_headers[col] = x # build column index
            else:
                # test column index
                if self.col_headers[col] != x:  
                    logging.warning('XYZ: column mismatch:'+self.col_headers[col]+" expected, got "+x)
            # build row headers ====
            if col == 0:
                self.row_headers[row] = y # build row index
            # build matrix
            self.matrix[row][col] = z # elevation in meters
            if (x == None) or (x <= 0):
                logging.warning("XYZ: illegal z value: "+z) 
            pass
        except ValueError as err:
            logging.error( err.args )
        pass

if __name__ == '__main__':
    print("This XYZ class module shall not be invoked on it's own.")