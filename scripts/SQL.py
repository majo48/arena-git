"""
    SQLite with Copernicus elevation data.
    N x 1200 x 1200 cells with geospatial coordinates and elevation data,
    each coordinate describes the centerpoint of the geospatial cell. 
    N is the numeber of tiles needed for arena.
"""

import sqlite3
import os
import math
import logging
from sqlite3.dbapi2 import Connection, Cursor

class SQL:

    def __init__(self, digits):
        """ 
            Initialize the SQL database 
        """
        self.digits = digits # number of significant digits for geolocation coordinates
        self.multiplier = 10 ** digits # same, see below in code
        # build database
        conn: Connection = self.__get_connection()
        cursor: Cursor = conn.cursor()
        try:
            # create table ...
            cursor.executescript("""
                PRAGMA foreign_keys=ON;
                CREATE TABLE IF NOT EXISTS matrix(
                    xIndex INTEGER,
                    yIndex INTEGER,
                    zVal INTEGER,
                    PRIMARY KEY (xIndex, yIndex)
                );  
                CREATE UNIQUE INDEX IF NOT EXISTS idx ON matrix (xIndex, yIndex);
            """)
            conn.commit()
            # close database cursor
            conn.close()
        except sqlite3.Error as e:
            logging.error("SQLite CREATE TABLE error occurred:" + e.args[0])
        pass

    def __enter__(self):
        """ 
            context manager 
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """ 
            context manager 
        """
        self.__get_connection().close()

    def __get_connection(self):
        """ 
            get SQLite connection object, create db file 
        """
        dbpath = os.path.dirname(os.path.realpath(__file__)) + '/db.sqlite3'
        return sqlite3.connect(dbpath)

    def set_matrix_cell(self, x: int, y: int, z: int):
        """ 
            set cell in database matrix x (lng east), y (lat north), z (elevation) 
        """
        conn: Connection = self.__get_connection()
        cursor: Cursor = conn.cursor()
        sql = """
            INSERT INTO matrix (xIndex, yIndex, zVal)
            VALUES(?,?,?)
        """
        try:
            cursor.execute( sql, (x, y, z))
            conn.commit()
        except sqlite3.Error as err:
            logging.error("SQLite INSERT error occured: "+ err.args[0])
        finally:
            conn.close()

    def get_nearest_neighbor(self, x: float, y: float):
        """ 
            get nearest xy cell value (z) from database matrix
        """
        pass


if __name__ == '__main__':
    print("This SQL class module shall not be invoked on it's own.")