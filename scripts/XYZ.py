"""
    XYZ with Copernicus elevation data.
    1200 x 1200 cells with geospatial coordinates and elevation data,
    the coordinates describe the centerpoint of the geospatial cell. 
"""

import os
import sys
import math
import logging
from SQL import SQL

# define elevation matrix for COG-90 (accuracy: < 4 meters)
EDGE = 1200 # matrix height (cols) and width (rows), equals cell size of 90 x 90 meters
MTRX = EDGE * EDGE # number of elements in matrix

class XYZ:
    def __init__(self, filename, db: SQL):
        self.db = db # SQLite3: database object, not implemented yet
        self.fctr = db.multiplier
        # build headers (fixed size)
        self.col_headers = [None]*EDGE # mutable
        self.row_headers = [None]*EDGE # mutable
        # build 2 dimensional array (fixed size)
        self.matrix = []  
        rows, cols = EDGE, EDGE
        for i in range(rows):
            col = bytearray([]) # mutable
            for j in range(cols):
                # set all cols == -1, 2 bytes per element
                col.append(255) # high byte (big endian)
                col.append(255) # low byte  (big endian)
            self.matrix.append(col)
        pass
        # convert text file to database 
        self.set_cells(filename) 

    def progress(self, count, total=MTRX, suffix=''):
        """ 
            display progress bar in console
        """
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))
        percents = round(100.0 * count / float(total), 3)
        bar = '=' * filled_len + '-' * (bar_len - filled_len)
        sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))
        sys.stdout.flush()  # As suggested by Rom Ruben

    def set_cells(self, filename):
        """
            read file and build matrix in the SQL database
            line: three numbers, sepatated with spaces
                longitude (9.xxx) in degrees east of Greenwich (G: Laengengrad) is X
                latitude (48.xxx) in degrees north of equator (G: Breitengrad) is Y
                elevation (714.xxx) in meters above sea level is Z
        """
        try:
            file = open(filename, "r")
            cnt = 0 
            self.progress(cnt)
            for row in range(EDGE):
                for col in range(EDGE):
                    line = file.readline()
                    if not line:
                        raise ValueError("Error in set_cells: premature end of file.")
                    if self.set_cell(row, col, line): 
                       raise ValueError("Error in set_cell: cannot add to database.")
                    cnt += 1 # increment success counter
                    if cnt % 100 == 0:
                        self.progress(cnt)
                    pass
                pass
            pass
        except ValueError as err:
            logging.error(err.args)
        finally:
            file.close()

    def set_cell(self, row, col, line):
        """
            convert line to XYZ cell item
        """
        try:
            # build cell, XYZ ====
            li = line.split(" ")
            x = int(float(li[0])*self.fctr)  # col index * 1000000 converted to int 
            y = int(float(li[1])*self.fctr)  # row index * 1000000 converted to int 
            z = int(float(li[2])) # elevation converted (rounded) to int meters
            z2b = z.to_bytes(2, byteorder='big') # elevation data up to 32'768 meters

            # update col headers ====
            if row == 0:
                self.col_headers[col] = x # update column index
            else:
                # test column index
                if self.col_headers[col] != x:  
                    logging.warning('XYZ: column mismatch:'+self.col_headers[col]+" expected, got "+x)

            # update row headers ====
            if col == 0:
                self.row_headers[row] = y # update row index

            # update matrix
            if (x == None) or (x <= 0):
                logging.warning("XYZ: illegal z value: "+z)
                # value in matrix == -1
            else:
                self.matrix[row][2*col] = z2b[0] # high byte, big endian
                self.matrix[row][2*col+1] = z2b[1] # low byte, big endian 
            pass
            quit = False
        #
        except ValueError as err:
            logging.error( err.args )
            quit = True
        finally:
            return quit

if __name__ == '__main__':
    print("This XYZ class module shall not be invoked on it's own.")