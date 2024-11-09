"""
Cache for rows of elevations, in order to speed up 'nearest_neighbour' queries
Contains also other variables apart from matrix rows
"""
MAXLENCACHE = 10 # max number of items in the cache


class Cache:

    
    def __init__(self):
        """
        Initialize the SQL cache
        """
        # local variables
        self._vars_set = False 
        self.col_headers = []  # empty list
        self.row_headers = []  # empty list
        self.bounding_box = {} # empty dictionary 
        self.row_span = 0.0    # floating var
        self.row_len = 0       # integer var
        self.col_span = 0.0    # floating var
        self.col_len = 0       # integer var
        self.cache = {}        # empty dictionary
        pass

    def isEmpty(self):
        """
        test if local variables are empty / set
        """
        return not self._vars_set

    def loadr(self, col_headers, row_headers, bounding_box):
        """
        set (local) variables for the first usage
        """
        self.col_headers = col_headers   # list of floating vars
        self.row_headers = row_headers   # list of floating vars
        self.bounding_box = bounding_box # dictionary var
        self.row_span = round(self.bounding_box['top']-self.bounding_box['bottom']) # floating var
        self.row_len = len(self.row_headers)                                        # integer var
        self.row_fctr = self.row_len/self.row_span                                  # multiplication factor
        self.col_span = round(self.bounding_box['right']-self.bounding_box['left']) # floating var
        self.col_len = len(self.col_headers)                                        # integer var
        self.col_fctr = self.col_len/self.col_span                                  # multiplication factor 
        self._vars_set = True
        pass

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

    def getRowFromCache(self, rowId):
        """
        get row[rowId] from the cache, else row is empty
        """
        if rowId in self.cache:
            return self.cache[rowId] # list with values
        else:
            return [] # empty list
        
    def addRowToCache(self, rowId, row):
        """
        add row[rowId] to the cache 
        """
        self.cache[rowId] = row
        if len(self.cache) > MAXLENCACHE:
            # delete oldest item from the cache
            oldest = next(iter(self.cache)) # ordered, needs Python version 3.7+
            del self.cache[oldest]
        pass        


# main ========

if __name__ == '__main__':
    print("This Cache class module shall not be invoked on it's own.")
        