"""
    SQLite with Copernicus elevation data.
    N x 1200 x 1200 cells with geospatial coordinates and elevation data,
    each coordinate describes the centerpoint of the geospatial cell. 
    N is the number of tiles needed for arena.
"""

import sqlite3
import logging
import pickle
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
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  colhdrs BLOB NOT NULL
                );
                CREATE TABLE IF NOT EXISTS main.rowhdrs(
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  rowhdrs BLOB NOT NULL
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

    # common functions ========

    def _delete_rows(self, tName):
        """
        delete all rows in table 'tName'
        """
        cursor: Cursor = self.conn.cursor()
        cursor.execute("DELETE FROM "+tName+";")
        self.conn.commit()

    # row headers ========

    def set_row_headers(self, row_headers):
        """
        set pickled row headers (latitudes aka Y, values ascending)
        """
        try:
            self._delete_rows("main.rowhdrs")
            sql = "INSERT INTO main.rowhdrs(rowhdrs) VALUES (?);"
            cursor: Cursor = self.conn.cursor()
            bData = pickle.dumps(row_headers, protocol=-1) # serialize row headers
            cursor.execute(sql, (bData,))
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error("SQLite INSERT TABLE rowhdrs error occurred:" + e.args[0])
        pass

    def get_row_headers(self):
        """
        get pickeled row headers (latitudes aka Y, values ascending)
        """
        try:
            sql = "SELECT rowhdrs FROM main.rowhdrs ORDER BY id DESC LIMIT 1;"
            cursor: Cursor = self.conn.cursor()
            cursor.execute(sql)
            rslt = pickle.loads(cursor.fetchone()[0]) # deserialize row headers
        except sqlite3.Error as e:
            logging.error("SQLite SELECT TABLE rowhdrs error occurred:" + e.args[0])
            rslt = []
        finally:
            return rslt

    # column headers ========

    def set_col_headers(self, col_headers):
        """
        set pickeled column headers (longitudes aka X, aka values ascending)
        """
        try:
            self._delete_rows("main.colhdrs")
            sql = "INSERT INTO main.colhdrs(colhdrs) VALUES (?);"
            cursor: Cursor = self.conn.cursor()
            bData = pickle.dumps(col_headers, protocol=-1) # serialize column headers
            cursor.execute(sql, (bData,))
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error("SQLite INSERT TABLE colhdrs error occurred:" + e.args[0])
        pass
    
    def get_col_headers(self):
        """
        get pickeled column headers (longitudes aka X, aka values ascending)
        """
        try:
            sql = "SELECT colhdrs FROM main.colhdrs ORDER BY id DESC LIMIT 1;"
            cursor: Cursor = self.conn.cursor()
            cursor.execute(sql)
            rslt = pickle.loads(cursor.fetchone()[0]) # deserialize column headers
        except sqlite3.Error as e:
            logging.error("SQLite SELECT TABLE colhdrs error occurred:" + e.args[0])
            rslt = []
        finally:
            return rslt

    # matrix ========
    def set_matrix(self, matrix: list, tilepath: str, tileinfo: str):
        """
        set matrix, all rows
        """
        try:
            self._delete_rows("main.rows")
            sql = "INSERT INTO main.rows(id, row) VALUES (?, ?);"
            cursor: Cursor = self.conn.cursor()
            # add each matrix row to empty table
            for idx in range(len(matrix)):
                cursor.execute(sql, (idx, matrix[idx]))
                self.conn.commit()
            pass
        except sqlite3.Error as e:
            logging.error("SQLite INSERT TABLE rows error occurred:" + e.args[0])
        pass

    def set_metadata(self, tilepath: str, tileinfo: str):
        """
        set metadata
        """
        try:
            self._delete_rows("main.metadata")
            sql = "INSERT INTO main.metadata(tilepath, tileinfo) VALUES (?, ?);"
            cursor: Cursor = self.conn.cursor()
            cursor.execute(sql, (tilepath, tileinfo))
            self.conn.commit()
            pass
        except sqlite3.Error as e:
            logging.error("SQLite INSERT TABLE metadata error occurred:" + e.args[0])
        pass

    def get_metadata(self):
        """
        get metadata
        """
        try:
            sql = "SELECT tilepath, tileinfo FROM main.metadata ORDER BY id DESC LIMIT 1;"
            cursor: Cursor = self.conn.cursor()
            cursor.execute(sql)
            rslt = cursor.fetchall()[0]
        except sqlite3.Error as e:
            logging.error("SQLite SELECT TABLE colhdrs error occurred:" + e.args[0])
            rslt = ()
        finally:
            return rslt # tuple, ('path', 'info')

    def get_matrix_row(self, rowId: int):
        """
        set matrix, one row with a binary list
        """
        raise Exception('WORK IN PROGRESS')

    def get_nearest_neighbor(self, lat: float, long: float):
        """ 
        get nearest xy cell value (z) from database matrix
        where: x == long, y == lat
        """
        return 417

# main ========

if __name__ == '__main__':
    print("This SQL class module shall not be invoked on it's own.")