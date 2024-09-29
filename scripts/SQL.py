"""
    SQLite with Copernicus elevation data.
    N x 1200 x 1200 cells with geospatial coordinates and elevation data,
    each coordinate describes the centerpoint of the geospatial cell. 
    N is the numeber of tiles needed for arena.
"""

import sqlite3
import logging
from sqlite3.dbapi2 import Connection, Cursor

class SQL:

    def __init__(self, dbpath, digits):
        """ 
            Initialize the SQL database 
        """
        self.dbpath = dbpath # location and name of database file
        self.multiplier = 10 ** digits # # number of significant digits for geolocation coordinates
        # build database
        self.conn: Connection = sqlite3.connect(dbpath)
        cursor: Cursor = self.conn.cursor()
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
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error("SQLite CREATE TABLE error occurred:" + e.args[0])
        pass

    def __enter__(self):
        """ 
            context manager: bigin session
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """ 
            context manager: end of session 
        """
        # close connection
        self.conn.close()

    def set_matrix_cell(self, x: int, y: int, z: int):
        """ 
            set cell in database matrix x (lng east), y (lat north), z (elevation) 
        """
        cursor: Cursor = self.conn.cursor()
        sql = """
            INSERT INTO matrix (xIndex, yIndex, zVal)
            VALUES(?,?,?)
        """
        try:
            cursor.execute( sql, (x, y, z))
            self.conn.commit()
        except sqlite3.Error as err:
            logging.error("SQLite INSERT error occured: "+ err.args[0])
        finally:
            pass

    def get_nearest_neighbor(self, x: float, y: float):
        """ 
            get nearest xy cell value (z) from database matrix
        """
        xIndex = int(x * self.multiplier) # normalized X index (longitude)
        yIndex = int(y * self.multiplier) # normalized Y index (latitude)
        raise Exception('Not implemented (yet).')


if __name__ == '__main__':
    print("This SQL class module shall not be invoked on it's own.")