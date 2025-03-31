"""
SQLite with Copernicus elevation data.
N x 1200 x 1200 cells with geospatial coordinates and elevation data.
    Each coordinate describes the center point of the geospatial cell.
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
            # conditionally create tables ...
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS colhdrs(
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  colhdrs BLOB NOT NULL
                );
                CREATE TABLE IF NOT EXISTS rowhdrs(
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  rowhdrs BLOB NOT NULL
                );
                CREATE TABLE IF NOT EXISTS rows(
                  id INTEGER PRIMARY KEY,
                  len INTEGER NOT NULL,
                  row BLOB NOT NULL
                );
                CREATE TABLE IF NOT EXISTS metadata(
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
            sql = "INSERT INTO rowhdrs(rowhdrs) VALUES (?);"
            cursor: Cursor = self.conn.cursor()
            b_data = pickle.dumps(row_headers, protocol=-1) # serialize row headers
            cursor.execute(sql, (b_data,))
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error("SQLite INSERT TABLE rowhdrs error occurred:" + e.args[0])
        pass

    def add_row_headers(self, row_headers):
        """
        add (append) pickled row headers (latitudes aka Y, values descending)
        tiles are added to the database from top(N) to bottom(S), left(W) to right(E)
        """
        try:
            # concatenate row headers
            rowhdrs = self.get_row_headers() + row_headers
            # remove original record
            sql = "DELETE FROM rowhdrs;" # delete all(one) record
            cursor: Cursor = self.conn.cursor()
            cursor.execute(sql)
            cursor.close()
            # write back concatenated row headers
            self.set_row_headers(rowhdrs)
            pass
        except sqlite3.Error as e:
            logging.error("SQLite ADD TO TABLE rowhdrs error occurred:" + e.args[0])
        pass

    def get_row_headers(self):
        """
        get row headers (latitudes aka Y, values descending)
        :return deserialized row headers
        """
        try:
            sql = "SELECT rowhdrs FROM rowhdrs ORDER BY id DESC LIMIT 1;"
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
        set pickled column headers (longitudes aka X, aka values ascending)
        """
        try:
            sql = "INSERT INTO colhdrs(colhdrs) VALUES (?);"
            cursor: Cursor = self.conn.cursor()
            b_data= pickle.dumps(col_headers, protocol=-1) # serialize column headers
            cursor.execute(sql, (b_data,))
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error("SQLite INSERT TABLE colhdrs error occurred:" + e.args[0])
        pass
    
    def add_col_headers(self, col_headers):
        """
        add (append) pickled column headers (longitudes aka X, values ascending)
        tiles are added to the database from top(N) to bottom(S), left(W) to right(E)
        """
        try:
            # concatenate column headers
            colhdrs = self.get_col_headers() + col_headers
            # remove original record
            sql = "DELETE FROM colhdrs;" # delete all(one) record
            cursor: Cursor = self.conn.cursor()
            cursor.execute(sql)
            cursor.close()
            # write back concatenated column headers
            self.set_col_headers(colhdrs)
            pass
        except sqlite3.Error as e:
            logging.error("SQLite ADD TO TABLE colhdrs error occurred:" + e.args[0])
        pass

    def get_col_headers(self):
        """
        get column headers (longitudes aka X, aka values ascending)
        :return deserialized column headers
        """
        try:
            sql = "SELECT colhdrs FROM colhdrs ORDER BY id DESC LIMIT 1;"
            cursor: Cursor = self.conn.cursor()
            cursor.execute(sql)
            rslt = pickle.loads(cursor.fetchone()[0]) # deserialize column headers
        except sqlite3.Error as e:
            logging.error("SQLite SELECT TABLE colhdrs error occurred:" + e.args[0])
            rslt = []
        return rslt

    # matrix ========

    def set_rows(self, matrix: list, pixel_top, pixel_left, max_bytes):
        """
        set(copy) all rows from the matrix to the database
        :return number of rows set, 0 is error
        """
        try:
            if pixel_left != 0:
                raise AssertionError("Illegal call to set_rows, use add_rows instead.")
            cursor: Cursor = self.conn.cursor()
            sql = "INSERT INTO rows(id, len, row) VALUES (?, ?, zeroblob(?));"
            bytes_len = len(matrix[0]) # size of one row, for Copernicus: 2400
            # add each matrix row to empty table
            idx = 0
            for idx in range(len(matrix)):
                db_index = idx+pixel_top
                cursor.execute(sql, (db_index, bytes_len, max_bytes)) # write zeroblob
                with self.conn.blobopen("rows", "row", db_index) as blob:
                    blob.write(matrix[idx]) # write one blob from matrix to zeroblob in database
                self.conn.commit()
            return idx
        except AssertionError as ae:
            logging.error(ae.args[0])
            return 0
        except sqlite3.Error as e:
            logging.error("SQLite set_rows error occurred: " + e.args[0])
            return 0

    def add_rows(self, matrix: list, pixel_top, pixel_left, max_bytes):
        """
        add(append) all rows from the matrix to the database
        :return number of rows added, 0 is error
        """
        try:
            if pixel_left == 0:
                raise AssertionError('Illegal call to add_rows, use set_rows instead.')
            cursor: Cursor = self.conn.cursor()
            sql = 'UPDATE rows SET len = ? WHERE id = ?;'
            offset = pixel_left*2 # two bytes per pixel
            new_len = offset + len(matrix[0])
            if new_len > max_bytes:
                raise AssertionError('Blob length exceeds the maximum allowed.')
            # append each matrix row to database table
            idx = 0
            for idx in range(len(matrix)):
                db_index = idx+pixel_top
                with self.conn.blobopen("rows", "row", db_index) as blob:
                    blob.seek(offset) # insert from here (offset)
                    blob.write(matrix[idx]) # write one blob from matrix to zeroblob in database
                self.conn.commit()
                # update new length in database
                cursor.execute(sql, (new_len, db_index))
                self.conn.commit()
            return idx
        except AssertionError as ae:
            logging.error(ae.args[0])
            return 0
        except sqlite3.Error as e:
            logging.error("SQLite add_rows error occurred:" + e.args[0])
            return 0

    def get_row(self, row_id):
        """
        get one row from the matrix in the database
        :return BLOB(bytearray)
        """
        try:
            sql = "SELECT id, len, row FROM rows WHERE ID = ?;"
            cursor: Cursor = self.conn.cursor()
            cursor.execute(sql, (row_id,))
            local_row = cursor.fetchone()
            bytes_len = local_row[1]
            rslt = local_row[2][:bytes_len]
        except sqlite3.Error as e:
            logging.error("SQLite SELECT TABLE row error occurred:" + e.args[0])
            rslt = bytearray() # empty bytearray
        return rslt

    # metadata ========

    def set_metadata_item(self, tilepath: str, tileinfo: str):
        """
        set metadata for one tile
        """
        try:
            sql = "INSERT INTO metadata(tilepath, tileinfo) VALUES (?, ?);"
            cursor: Cursor = self.conn.cursor()
            cursor.execute(sql, (tilepath, tileinfo))
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error("SQLite INSERT TABLE metadata error occurred:" + e.args[0])
        pass

    def get_metadata_items(self):
        """
        get all metadata records
        """
        try:
            sql = "SELECT tilepath, tileinfo FROM metadata ORDER BY id ASC;"
            cursor: Cursor = self.conn.cursor()
            cursor.execute(sql)
            return cursor.fetchall() # list, ('path', 'info')
        except sqlite3.Error as e:
            logging.error("SQLite SELECT TABLE colhdrs error occurred:" + e.args[0])
            return []

    def get_arena_bounding_box(self):
        """
        calculate the total bounding box from all tile metadata items
        """
        abb_len = len(self.get_metadata_items())
        if abb_len>0:
            # initial values
            meta = json.loads(self.get_metadata_items()[0][1])
            top = meta["top"]
            bottom = meta["bottom"]
            left = meta["left"]
            right = meta["right"]
            # find maximum values
            for idx in range(1, abb_len):
                meta = json.loads(self.get_metadata_items()[idx][1])
                if meta["top"] > top: top = meta["top"]
                if meta["bottom"] < bottom: bottom = meta["bottom"]
                if meta["left"] < left: left = meta["left"]
                if meta["right"] > right: right = meta["right"]
            pass
            return {"top": top, "bottom": bottom, "left": left, "right": right}
        raise AssertionError('Empty metadata-list in the arena bounding box.')

# main ========

if __name__ == '__main__':
    print("The SQL class module shall not be invoked on it's own.")