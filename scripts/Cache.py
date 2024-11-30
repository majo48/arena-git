"""
Cache for rows of elevations, in order to speed up 'nearest_neighbour' queries
Contains also other variables apart from matrix rows
"""

# packages
from SQL import SQL
import json
import logging
import math
from math import radians, sin, cos, acos

# constants
MAXLENCACHE = 10 # max number of items in the cache


class Cache:
    
    def __init__(self, dbpath):
        """
        Initialize the SQL cache
        """
        self.sqldb = SQL(dbpath)
        self.row_headers = self.sqldb.get_row_headers()
        self.col_headers = self.sqldb.get_col_headers()
        self.bounding_box = json.loads(self.sqldb.get_metadata()[1])
        self.row_span = round(self.bounding_box['top']-self.bounding_box['bottom']) # floating var
        self.row_len = len(self.row_headers)                                        # integer var
        self.row_fctr = self.row_len/self.row_span                                  # multiplication factor
        self.col_span = round(self.bounding_box['right']-self.bounding_box['left']) # floating var
        self.col_len = len(self.col_headers)                                        # integer var
        self.col_fctr = self.col_len/self.col_span                                  # multiplication factor 
        self.cache = {}                                                             # dictionary with unpickeled rows
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
        del self.sqldb

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
            rslt = self.sqldb.get_row(rowId)
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

    def _get_cell(self, rowId, colId):
        """ 
        get the cell value (z, elevation) from the database matrix
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

    def get_nearest_neighbor(self, lat: float, long: float):
        """ 
        get nearest xy cell value (z, elevation profile data) from the database matrix
        where: x == long, y == lat, returns the elevation in meters (-1 is error)
        """
        if not self.inScope(lat, long):
            logging.warning("Query for 'nearest neighbour' is out of scope: ("+str(lat)+", "+str(long)+")")
            return {} # empty
        try:
            rowId, colId = self.getDimensions(lat, long)
            return self._get_cell( rowId, colId)
        except Exception as err:
            logging.error("Get nearest neighbour error: "+str(err.args))
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
    print("This Cache class module shall not be invoked on it's own.")
        