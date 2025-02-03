#!/usr/bin/env python3

"""
    test the length of byte arrays
"""

# packages ========
import random
import sys

# constants ========
EDGE = 1200 # resolution of the Copernicus GLO-90 DSM

# main ========

def build_matrix(rows, cols):
    """
    build matrix
    :return: matrix (list)
    """
    matrix = []
    for i in range(rows):
        col = bytearray([])  # mutable
        for j in range(cols):
            # set all cols == -1, 2 bytes per element
            col.append(255)  # high byte (big endian)
            col.append(255)  # low byte  (big endian)
        matrix.append(col)
    pass
    # fill matrix with random elevations
    for i in range(rows):
        for j in range(cols):
            z = random.randint(0, 8849)
            z2b = z.to_bytes(2, byteorder='big')
            matrix[i][2*j] = z2b[0] # high byte
            matrix[i][2*j+1] = z2b[1] # low byte
    pass # end for
    return matrix

rows = EDGE
cols = EDGE
for i in range(1, 30):
    mtrx = build_matrix(rows, i*cols)
    print("Matrix: row items=", str(i*cols), ", size of one row in bytes=", sys.getsizeof(mtrx[0]), "F:", round(sys.getsizeof(mtrx[0])/(i*cols), 3))
pass
exit(0)
# OUTPUT: F(max) = 2.239
"""
    Matrix: row items= 1200 , size of one row in bytes= 2458 F: 2.048
    Matrix: row items= 2400 , size of one row in bytes= 4971 F: 2.071
    Matrix: row items= 3600 , size of one row in bytes= 7956 F: 2.21
    Matrix: row items= 4800 , size of one row in bytes= 10066 F: 2.097
    Matrix: row items= 6000 , size of one row in bytes= 12737 F: 2.123
    Matrix: row items= 7200 , size of one row in bytes= 16118 F: 2.239
    Matrix: row items= 8400 , size of one row in bytes= 18131 F: 2.158
    Matrix: row items= 9600 , size of one row in bytes= 20396 F: 2.125
    Matrix: row items= 10800 , size of one row in bytes= 22944 F: 2.124
    Matrix: row items= 12000 , size of one row in bytes= 25811 F: 2.151
    Matrix: row items= 13200 , size of one row in bytes= 29036 F: 2.2
    Matrix: row items= 14400 , size of one row in bytes= 29036 F: 2.016
    Matrix: row items= 15600 , size of one row in bytes= 32664 F: 2.094
    Matrix: row items= 16800 , size of one row in bytes= 36746 F: 2.187
    Matrix: row items= 18000 , size of one row in bytes= 36746 F: 2.041
    Matrix: row items= 19200 , size of one row in bytes= 41338 F: 2.153
    Matrix: row items= 20400 , size of one row in bytes= 41338 F: 2.026
    Matrix: row items= 21600 , size of one row in bytes= 46504 F: 2.153
    Matrix: row items= 22800 , size of one row in bytes= 46504 F: 2.04
    Matrix: row items= 24000 , size of one row in bytes= 52316 F: 2.18
    Matrix: row items= 25200 , size of one row in bytes= 52316 F: 2.076
    Matrix: row items= 26400 , size of one row in bytes= 58854 F: 2.229
    Matrix: row items= 27600 , size of one row in bytes= 58854 F: 2.132
    Matrix: row items= 28800 , size of one row in bytes= 58854 F: 2.044
    Matrix: row items= 30000 , size of one row in bytes= 66209 F: 2.207
    Matrix: row items= 31200 , size of one row in bytes= 66209 F: 2.122
    Matrix: row items= 32400 , size of one row in bytes= 66209 F: 2.043
    Matrix: row items= 33600 , size of one row in bytes= 74484 F: 2.217
    Matrix: row items= 34800 , size of one row in bytes= 74484 F: 2.14

    Process finished with exit code 0
"""
