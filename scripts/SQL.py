"""
    SQLite with Copernicus elevation data.
    N x 1200 x 1200 cells with geospatial coordinates and elevation data,
    each coordinate describes the centerpoint of the geospatial cell. 
    N is the number of tiles needed for arena.
"""

import sqlite3
from sqlite3.dbapi2 import Connection, Cursor
import logging
import pickle
import json
import math
from math import radians, sin, cos, acos
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
            self.cache.set_empty() # invalidate cache
        except sqlite3.Error as e:
            logging.error("SQLite INSERT TABLE rowhdrs error occurred:" + e.args[0])
        pass

    def get_row_headers(self):
        """
        get pickeled row headers (latitudes aka Y, values ascending)
        """
        rslt = self.cache.get_row_headers()
        if not rslt: # empty cache
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
            self._delete_rows("main.colhdrs")
            sql = "INSERT INTO main.colhdrs(colhdrs) VALUES (?);"
            cursor: Cursor = self.conn.cursor()
            bData = pickle.dumps(col_headers, protocol=-1) # serialize column headers
            cursor.execute(sql, (bData,))
            self.conn.commit()
            self.cache.set_empty() # invalidate cache
        except sqlite3.Error as e:
            logging.error("SQLite INSERT TABLE colhdrs error occurred:" + e.args[0])
        pass
    
    def get_col_headers(self):
        """
        get pickeled column headers (longitudes aka X, aka values ascending)
        """
        rslt = self.cache.get_col_headers()
        if not rslt: # empty cache
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
            self._delete_rows("main.rows")
            sql = "INSERT INTO main.rows(id, row) VALUES (?, ?);"
            cursor: Cursor = self.conn.cursor()
            # add each matrix row to empty table
            for idx in range(len(matrix)):
                cursor.execute(sql, (idx, matrix[idx]))
                self.conn.commit()
            pass
            self.cache.set_empty() # invalidate cache
        except sqlite3.Error as e:
            logging.error("SQLite INSERT TABLE rows error occurred:" + e.args[0])
        pass

    def get_row(self, rowId):
        """
        get one row from the matrix
        """
        rslt = self.cache.getRowFromCache(rowId)
        if not rslt: # empty cache
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
            self.cache.set_empty() # invalidate cache
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
    def _getLat(self, rowId: int):
        """
        Get the latitude which corresponds with the id
        """
        return self.get_row_headers()[rowId]

    def _getLong(self, colId: int):
        """
        Get the longitude which corresponds with the id
        """
        return self.get_col_headers()[colId]

    def _get_distance_old(self, point1, point2):
        """
        Use the pythagoras formula to calculate approx. distance between two points.
        Each point is a (lat, long) tuple, the distance is in degrees.
        Not exact, but sufficiant for weighting elevations.
        """
        a = point1[0]-point2[0] # lat difference
        b = point1[1]-point2[1] # long difference
        return math.sqrt(a**2 + b**2) 

    def _get_distance(self, fromPlace: tuple, toPlace: tuple):
        """
        Calculate the distance (in meters) between two points on the globe (haversine formula)
        """
        mlat = radians(fromPlace[0])
        mlon = radians(fromPlace[1])
        plat = radians(toPlace[0])
        plon = radians(toPlace[1])
        dist = 6371.01 * acos(sin(mlat)*sin(plat) + cos(mlat)*cos(plat)*cos(mlon - plon))
        return int(dist*1000) # distance in meters

    def _loadr(self):
        """
        Load cache with starting values
        """
        self.cache.loadr(
                self.get_col_headers(),
                self.get_row_headers(),
                json.loads(self.get_metadata()[1])
        )
        pass

    def _get_cell(self, rowId, colId):
        """ 
        get the cell value (z, elevation) from the database matrix
        with rowId (y, lat) and colId (X, long)
        returns the elevation in meters (-1 is error)
        """
        try:
            # get binary elevation data 
            row = self.get_row(rowId) # row data (binary)
            col2 = 2*colId # offset in row
            bytes = row[col2:col2+2]
            elevation = int.from_bytes(bytes, "big")
            return { 
                "elevtn":elevation, 
                "rowId": rowId, "colId": colId, 
                "lat": self._getLat(rowId), "long": self._getLong(colId) 
            }
        except Exception as err:
            logging.error("Get matrix cell error: "+err.args)
            return {} # empty

    def get_nearest_neighbor(self, lat: float, long: float):
        """ 
        get nearest xy cell value (z, elevation profile data) from the database matrix
        where: x == long, y == lat, returns the elevation in meters (-1 is error)
        """
        if self.cache.isEmpty(): 
            self._loadr()
        if not self.cache.inScope(lat, long):
            logging.warning("Query for 'nearest neighbour' is out of scope: ("+str(lat)+", "+str(long)+")")
            return {} # empty
        try:
            rowId, colId = self.cache.getDimensions(lat, long)
            return self._get_cell( rowId, colId)
        except Exception as err:
            logging.error("Get nearest neighbour error: "+err.args)
            return {} # empty

    def get_weighted_elevation(self, lat: float, long: float):
        """
        Get the weighted elevation in meters, using nine cells: 
            nearest, north, south, west, east, northwest, northeast, southwest, southeast 
        """
        nearest = self.get_nearest_neighbor(lat, long)
        if not nearest: # empty
            return -1   # error has already been logged
        # get neighbouring cells (spaced 90 meters apart)
        try:
            # same row as nearest
            west = self._get_cell( nearest["rowId"], nearest["colId"]-1 )
            east = self._get_cell( nearest["rowId"], nearest["colId"]+1 )
            # upper row
            north = self._get_cell( nearest["rowId"]+1, nearest["colId"] )
            northwest = self._get_cell( nearest["rowId"]+1, nearest["colId"]-1 )
            northeast = self._get_cell( nearest["rowId"]+1, nearest["colId"]+1 )
            # lower row
            south = self._get_cell( nearest["rowId"]-1, nearest["colId"] )
            southwest = self._get_cell( nearest["rowId"]-1, nearest["colId"]-1 )
            southeast = self._get_cell( nearest["rowId"]-1, nearest["colId"]+1 )
            # calculate weighted elevation, weighted by distance vectors
            elevations_and_weights = [
                (nearest["elevtn"], self._get_distance( (lat, long), (nearest["lat"], nearest["long"]))),
                (west["elevtn"], self._get_distance( (lat, long), (west["lat"], west["long"]))),
                (east["elevtn"], self._get_distance( (lat, long), (east["lat"], east["long"]))),
                (north["elevtn"], self._get_distance( (lat, long), (north["lat"], north["long"]))),
                (northwest["elevtn"], self._get_distance( (lat, long), (northwest["lat"], northwest["long"]))),
                (northeast["elevtn"], self._get_distance( (lat, long), (northeast["lat"], northeast["long"]))),
                (south["elevtn"], self._get_distance( (lat, long), (south["lat"], south["long"]))),
                (southwest["elevtn"], self._get_distance( (lat, long), (southwest["lat"], southwest["long"]))),
                (southeast["elevtn"], self._get_distance( (lat, long), (southeast["lat"], southeast["long"])))
            ]
            sum_weights = 0.0
            sum_products = 0.0
            for eaw in elevations_and_weights:
                sum_weights += 1/eaw[1]
                sum_products += eaw[0]/eaw[1]
            weighted_elevation = sum_products / sum_weights
            return int(weighted_elevation)
        except ZeroDivisionError as err:
            logging.error("Get weighted elevation zero division error: "+err.args)
        except LookupError as err:
            logging.error("Get weighted elevation look up error: "+err.args)
        except Exception as err:
            logging.error("Get weighted elevation unknown error: "+err.args)
        finally:
            return nearest["elevtn"] # The best possible and probable answer
        
# main ========

if __name__ == '__main__':
    print("The SQL class module shall not be invoked on it's own.")