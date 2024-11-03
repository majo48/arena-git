"""
    SQLite with Copernicus elevation data.
    N x 1200 x 1200 cells with geospatial coordinates and elevation data,
    each coordinate describes the centerpoint of the geospatial cell. 
    N is the number of tiles needed for arena.
"""

import sqlite3
import logging
import pickle
import json
from sqlite3.dbapi2 import Connection, Cursor
from Cache import Cache

class SQL:

    def __init__(self, dbpath):
        """ 
        Initialize the SQL database 
        """
        self.dbpath = dbpath # location and name of database file
        self.cache = Cache() # empty cache and bounding box
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
        # close connection
        self.conn.close()
        # close cache
        del self.cache

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
    def set_rows(self, matrix: list, tilepath: str, tileinfo: str):
        """
        set all rows in matrix
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

    def get_row(self, rowId):
        """
        get one row of the matrix
        """
        rslt = self.cache.getRowFromCache(rowId)
        if not rslt: 
            # empty list, not in cache
            try:
                sql = "SELECT * FROM main.rows WHERE ID = ?;"
                cursor: Cursor = self.conn.cursor()
                cursor.execute(sql, (rowId, ))
                rslt = cursor.fetchone()[1]
                self.cache.addRowToCache(rowId, rslt)
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

    # elevation data ========
    def _getX(self, idx: float):
        """
        Get the latitude for the id
        """
        id = round(idx)
        return self.local_row_headers[id]

    def _getY(self, idy: float):
        """
        Get the longitude for the id
        """
        id = round(idy)
        return self.local_col_headers[id]

    def get_nearest_neighbor(self, lat: float, long: float):
        """ 
        get nearest xy cell value (z, elevation profile data) from the database matrix
        where: x == long, y == lat, returns the elevation in meters (-1 is error)
        """
        if self.cache.isEmpty(): 
            self.cache.loadr(
                self.get_col_headers(),
                self.get_row_headers(),
                json.loads(self.get_metadata()[1])
            )
        if not self.cache.inScope(lat, long):
            logging.warning("Query for 'nearest neighbour' is out of scope: ("+str(lat)+", "+str(long)+")")
            return { "elevtn":-1, "rowId": -1, "colId": -1 }
        try:
            # get binary elevation data 
            rowId, colId = self.cache.getDimensions(lat, long)
            row = self.get_row(rowId) # row data (binary)
            col2 = 2*colId # offset in row
            bytes = row[col2:col2+2]
            elevation = int.from_bytes(bytes, "big")
            return { "elevtn":elevation, "rowId": rowId, "colId": colId }
        except Exception as err:
            logging.error("Get nearest neighbour error: "+err.args)
            return { "elevtn":-1, "rowId": -1, "colId": -1 }

# main ========

if __name__ == '__main__':
    print("The SQL class module shall not be invoked on it's own.")