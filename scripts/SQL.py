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

    def __init__(self, dbpath):
        """ 
        Initialize the SQL database 
        """
        self.dbpath = dbpath # location and name of database file
        # build database
        self.conn: Connection = sqlite3.connect(dbpath)
        cursor: Cursor = self.conn.cursor()
        try:
            # create table ...
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS main.colhdrs(
                  id INTEGER PRIMARY KEY,
                  colhdr REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS main.rowhdrs(
                  id INTEGER PRIMARY KEY,
                  rowhdr REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS main.rows(
                  id INTEGER PRIMARY KEY,
                  row BLOB NOT NULL
                );
                CREATE TABLE IF NOT EXISTS main.metadata(
                  id INTEGER PRIMARY KEY,
                  tilepath TEXT NOT NULL,
                  tileinfo TEXT NOT NULL
                );
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error("SQLite CREATE TABLE error occurred:" + e.args[0])
        pass

    # context manager ========

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

    # row headers ========

    def set_row_headers(self, row_headers):
        """
        set row headers (latitudes aka Y, values ascending)
        """
        for i in range(len(row_headers)):
            pass
        pass

    def get_row_headers(self):
        """
        get row headers (latitudes aka Y, values ascending)
        """
        return []

    # column headers ========

    def set_col_headers(self, col_headers):
        """
        set column headers (longitudes aka X, aka values ascending)
        """
        for i in range(len(col_headers)):
            pass
        pass
    
    def get_col_headers(self):
        """
        get column headers (longitudes aka X, aka values ascending)
        """
        return []

    # matrix ========
    def set_matrix(self, matrix: list, tilepath: str, tileinfo: str):
        """
        set matrix, all rows
        """
        for i in range(len(matrix)):
            pass
        pass

    def get_matrix_row(self, rowId: int):
        """
        set matrix, one row with a binary list
        """
        return []

    def get_nearest_neighbor(self, x: float, y: float):
        """ 
        get nearest xy cell value (z) from database matrix
        """
        raise Exception('WORK IN PROGRESS')

# main ========

if __name__ == '__main__':
    print("This SQL class module shall not be invoked on it's own.")