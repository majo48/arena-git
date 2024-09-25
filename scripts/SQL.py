"""
    SQLite with Copernicus elevation data.
    N x 1200 x 1200 cells with geospatial coordinates and elevation data,
    each coordinate describes the centerpoint of the geospatial cell. 
    N is the numeber of tiles needed for arena.
"""

import sqlite3
import os
import logging
from sqlite3.dbapi2 import Connection, Cursor

class SQL:

    def __init__(self):
        """ Initialize the SQL database """
        conn: Connection = self.__get_connection()
        cursor: Cursor = conn.cursor()
        try:
            # create table ...
            cursor.execute("""
                PRAGMA foreign_keys=ON;
                CREATE TABLE IF NOT EXISTS matrix(
                    xIndex INTEGER,
                    yIndex INTEGER,
                    zVal INTEGER,
                    PRIMARY KEY (xIndex, yIndex)
                );  
                CREATE UNIQUE INDEX IF NOT EXISTS index ON matrix (xIndex, yIndex);
            """)
            conn.commit()
            # close database cursor
            conn.close()
        except sqlite3.Error as e:
            logging.error("SQLite CREATE TABLE error occurred:" + e.args[0])
        pass

    def __get_connection(self):
        """ get SQLite connection object """
        logpath = os.path.dirname(os.path.realpath(__file__))
        endpath = logpath.split('/')[-1]
        dbpath = logpath.replace('/' + endpath, '/database/db.sqlite3')
        return sqlite3.connect(dbpath)

    def set_matrix_cell(self, x, y, z):
        """ set cell in matrix x (lng east), y (lat north), z (elevation) """
        pass

    def get_nearest_cell(self, x, y):
        """ get nearest cell value from matrix """
        pass


if __name__ == '__main__':
    print("This SQL class module shall not be invoked on it's own.")