"""
SQLite with Copernicus elevation data.
N x 1200 x 1200 cells with geospatial coordinates and elevation data.
    Each coordinate describes the centerpoint of the geospatial cell.
    N is the number of tiles needed for arena.
"""

import sqlite3
from sqlite3.dbapi2 import Connection, Cursor
import logging
import pickle
import json

class Dbsql:

    def __init__(self, dbpath):
        """ 
        Initialize the SQL database 
        """
        self.dbpath = dbpath # location and name of database file
        #
        # build database
        self.conn: Connection = sqlite3.connect(dbpath)
        cursor: Cursor = self.conn.cursor()
        try:
            # create tables ...
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
        self.conn.close() # close connection

    # row headers ========

    def set_row_headers(self, row_headers):
        """
        set pickled row headers (latitudes aka Y, values descending)
        """
        try:
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
        get pickeled row headers (latitudes aka Y, values descending)
        """
        try:
            sql = "SELECT rowhdrs FROM main.rowhdrs ORDER BY id DESC LIMIT 1;"
            cursor: Cursor = self.conn.cursor()
            cursor.execute(sql)
            rslt = pickle.loads(cursor.fetchone()[0]) # deserialize row headers
        except sqlite3.Error as e:
            logging.error("SQLite SELECT TABLE rowhdrs error occurred:" + e.args[0])
            rslt = []
        return rslt

    # column headers ========

    def set_col_headers(self, col_headers):
        """
        set pickeled column headers (longitudes aka X, aka values ascending)
        """
        try:
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
        return rslt

    # matrix ========

    def set_rows(self, matrix: list, tilepath: str, tileinfo: str):
        """
        set all rows in matrix
        """
        try:
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

    def get_row(self, rowId):
        """
        get one row from the matrix in the database
        """
        try:
            sql = "SELECT * FROM main.rows WHERE ID = ?;"
            cursor: Cursor = self.conn.cursor()
            cursor.execute(sql, (rowId, ))
            rslt = cursor.fetchone()[1]
        except sqlite3.Error as e:
            logging.error("SQLite SELECT TABLE rows error occurred:" + e.args[0])
            rslt = []
        return rslt

    # metadata ========

    def set_metadata(self, tilepath: str, tileinfo: str):
        """
        set metadata
        """
        try:
            sql = "INSERT INTO main.metadata(tilepath, tileinfo) VALUES (?, ?);"
            cursor: Cursor = self.conn.cursor()
            cursor.execute(sql, (tilepath, tileinfo))
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error("SQLite INSERT TABLE metadata error occurred:" + e.args[0])
        pass

    def get_metadata(self):
        """
        get all metadata records
        """
        try:
            sql = "SELECT tilepath, tileinfo FROM main.metadata ORDER BY id ASC;"
            cursor: Cursor = self.conn.cursor()
            cursor.execute(sql)
            rslt = cursor.fetchall()
        except sqlite3.Error as e:
            logging.error("SQLite SELECT TABLE colhdrs error occurred:" + e.args[0])
            rslt = ()
        finally:
            return rslt # list, ('path', 'info')

    def get_bounding_box(self):
        """
        calculate the total bounding box from all metadata items
        """
        for key, value in enumerate(self.get_metadata()):
            meta = json.loads(value[1])
            if key == 0:
                top = meta["top"]
                bottom = meta["bottom"]
                left = meta["left"]
                right = meta["right"]
            else: # key > 0
                if meta["top"] > top: top = meta["top"]
                if meta["bottom"] < bottom: bottom = meta["bottom"]
                if meta["left"] < left: left = meta["left"]
                if meta["right"] > right: right = meta["right"]
            pass
        pass
        return {"top": top, "bottom": bottom, "left": left, "right": right}


# main ========

if __name__ == '__main__':
    print("The SQL class module shall not be invoked on it's own.")