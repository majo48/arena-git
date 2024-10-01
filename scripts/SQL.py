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
                CREATE TABLE IF NOT EXISTS main.colhdrs(
                  id INTEGER PRIMARY KEY ASC,
                  colhdr INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS main.rowhdrs(
                  id INTEGER PRIMARY KEY ASC,
                  rowhdr INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS main.rows(
                  id INTEGER PRIMARY KEY ASC,
                  row BLOB NOT NULL
                );
                CREATE TABLE IF NOT EXISTS main.metadata(
                  id INTEGER PRIMARY KEY ASC,
                  tilepath TEXT NOT NULL,
                  moreinfo TEXT
                );
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error("SQLite CREATE TABLE error occurred:" + e.args[0])
        pass

    def __enter__(self):
        """ 
        context manager: begin session
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
            raise Exception('DEPRECIATED')
            cursor.execute( sql, (x, y, z))
            self.conn.commit()
        except sqlite3.Error as err:
            logging.error("SQLite INSERT error occured: "+ err.args[0])
        finally:
            pass

    def set_row_headers(self, row_headers):
        """
        set row headers (latitudes aka Y, values ascending)
        """
        for i in range(len(row_headers)):
            pass
        pass

    def set_col_headers(self, col_headers):
        """
        set column headers (longitudes aka X, aka values ascending)
        """
        for i in range(len(col_headers)):
            pass
        pass
    
    def set_matrix_cells(self, bList):
        """ 
        set matrix, all cells    
        """
        for i in range(len(bList)):
            pass
        pass

    def get_nearest_neighbor(self, x: float, y: float):
        """ 
        get nearest xy cell value (z) from database matrix
        """
        xIndex = int(x * self.multiplier) # normalized X index (longitude)
        yIndex = int(y * self.multiplier) # normalized Y index (latitude)
        raise Exception('WORK IN PROGRESS')


if __name__ == '__main__':
    print("This SQL class module shall not be invoked on it's own.")