"""
Cache for rows of elevations, in order to speed up 'nearest_neighbour' queries
Contains also other variables apart from matrix rows
"""

# packages
from Dbsql import Dbsql
import json
import logging
import math
from math import radians, sin, cos, acos

# constants
MAXLENCACHE = 10 # max number of items in the cache
NEXTCELLS = {
    "NW":(1,-1), "N":(1,0), "NE":(1,1), 
    "W":(0,-1), "E":(0,1), 
    "SW":(-1,-1), "S":(-1,0), "SE":(-1,1)
}


class Dbcache:
    
    def __init__(self, dbpath):
        """
        Initialize the SQL cache
        """
        self.dbsql = Dbsql(dbpath)
        self.row_headers = self.dbsql.get_row_headers()
        self.col_headers = self.dbsql.get_col_headers()
        self.bounding_box = self.dbsql.get_arena_bounding_box()
        self.row_span = round(self.bounding_box['top']-self.bounding_box['bottom']) # floating var
        self.row_len = len(self.row_headers)                                        # integer var
        self.row_fctr = self.row_len/self.row_span                                  # multiplication factor
        self.col_span = round(self.bounding_box['right']-self.bounding_box['left']) # floating var
        self.col_len = len(self.col_headers)                                        # integer var
        self.col_fctr = self.col_len/self.col_span                                  # multiplication factor 
        self.cache = {}                                                             # dictionary with unpickeled rows
        self.last_position = None                                                   # tuple (lat, long) or None
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
        # close database
        del self.dbsql

    # validate ========

    def inScope(self, lat, long):
        """
        check if coordinates (lat,long) is inside the scope of the bounding box
            True:   OK, inside bounding box
            False:  outside of scope 
        """
        # check latitude
        Y = (lat <= self.bounding_box['top']) and (lat >= self.bounding_box['bottom'])
        # check longitude
        X = (long >= self.bounding_box['left']) and (long <= self.bounding_box['right']) 
        return Y and X

    # convert ========

    def getDimensions(self, lat, long):
        """
        convert geoposition (lat, long) to array dimensions (row, col)
        """
        rowId = round((self.bounding_box['top'] - lat)*self.row_fctr)
        colId = round((long - self.bounding_box['left'])*self.col_fctr)
        return rowId, colId

    # cache ========

    def _getRowFromCache(self, rowId):
        """
        get row[rowId] from the cache, else row is empty
        """
        if rowId in self.cache:
            return self.cache[rowId] # list with values
        else:
            return [] # empty list
        
    def _addRowToCache(self, rowId, row):
        """
        add row[rowId] to the cache 
        """
        self.cache[rowId] = row
        if len(self.cache) > MAXLENCACHE:
            # delete oldest item from the cache
            oldest = next(iter(self.cache)) # ordered, needs Python version 3.7+
            del self.cache[oldest]
        pass        

    def _get_either_row(self, rowId):
        """
        get row[rowId] from either the cache or the database
        """
        rslt = self._getRowFromCache(rowId)
        if not rslt: # empty cache
            rslt = self.dbsql.get_row(rowId)
            self._addRowToCache(rowId, rslt)
        return rslt

    # elevation data ========

    def _getLat(self, rowId: int):
        """
        Get the latitude which corresponds with the id
        """
        return self.row_headers[rowId]

    def _getLong(self, colId: int):
        """
        Get the longitude which corresponds with the id
        """
        return self.col_headers[colId]

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

    def _get_elevation(self, rowId, colId):
        """ 
        Get the cell value (z, elevation) from the database matrix
        with rowId (y, lat) and colId (X, long)
        returns the elevation in meters (-1 is error)
        """
        try:
            # get binary elevation data 
            row = self._get_either_row(rowId) # row data (binary)
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

    def _get_direction(self, lat, long):
        """
        Give the direction going from self.last_position to (lat, long)
        """
        if not self.last_position: # is empty
            self.last_position = (lat, long)
            return None, None
        deltaX = long - self.last_position[1] # longitude
        deltaY = lat - self.last_position[0]  # latitude
        degrees_temp = math.atan2(deltaX, deltaY)/math.pi*180
        if degrees_temp < 0:
            degrees_final = 360 + degrees_temp
        else:
            degrees_final = degrees_temp
        compass_brackets = ["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"]
        compass_lookup = round(degrees_final / 45)
        self.last_position = (lat, long) # save position
        return compass_brackets[compass_lookup], degrees_final

    def _get_nearest_elevation(self, lat: float, long: float):
        """ 
        Get nearest xy cell value (z, elevation profile data) from the database matrix
        where: x == long, y == lat, returns the elevation in meters (-1 is error)
        """
        if not self.inScope(lat, long):
            logging.warning("Query for 'nearest neighbour' is out of scope: ("+str(lat)+", "+str(long)+")")
            return {} # empty
        try:
            rowId = round((self.bounding_box['top'] - lat)*self.row_fctr) # ordered descending
            colId = round((long - self.bounding_box['left'])*self.col_fctr) # ordered ascending
            return self._get_elevation(rowId, colId)
        except Exception as err:
            logging.error("Get nearest neighbour error: "+str(err.args))
            return {} # empty

    def get_elevation(self, lat: float, long: float):
        """
        Get the elevation in meters (integer)
        """
        nearest = self._get_nearest_elevation(lat, long)
        if not nearest: # empty
            return -1   # error has already been logged
        else:
            return nearest["elevtn"]
        
    def get_flight_information(self, lat: float, long: float):
        """
        Get flight information:
        - the elevation in meters (integer) of the current location, 
        - the elevation of the next cell in flying direction, 
        - the direction (N, S, E, W, NW, NE, SW, SE),
        - the compass heading (0 .. 360 degrees).
        Notes:
            Each cell is 90 x 90 meters in the digital surface model (DSM).
            The DSM does not include buildings, towers or other such objects.
        """
        nearest = self._get_nearest_elevation(lat, long)
        if not nearest:   # empty
            return -1, -1, None, None # error has already been logged
        try:
            currentElevation = nearest["elevtn"]
            # get direction
            direction, compass = self._get_direction(lat, long)
            if not direction: # is empty
                return currentElevation, currentElevation, None, None
            # get next cell in flying direction
            rowId = nearest["rowId"] + NEXTCELLS[direction][0]
            colId = nearest["colId"] + NEXTCELLS[direction][1]
            nextCell = self._get_elevation(rowId, colId)
            nextElevation = nextCell["elevtn"]
            return currentElevation, nextElevation, direction, round(compass, 2)
        except Exception as err:
            logging.error("Get elevations, unknown error: "+err.args)
            return currentElevation, currentElevation, None, None


# main ========

if __name__ == '__main__':
    print("This Cache class module shall not be invoked on it's own.")
        