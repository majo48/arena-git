#!/usr/bin/env python3

"""
    test the usage of SQLite3 'zeroblob' concept
        prerequisite: Python version 3.11+
        reference: https://docs.python.org/3/library/sqlite3.html
"""

# packages ========
import random
import os
import sqlite3
from sqlite3.dbapi2 import Connection, Cursor
from decouple import config

# constants ========
EDGE = 1200 # resolution of the Copernicus GLO-90 DSM
FACTOR = 2.4

# global var ========
idx_len_list = [0]  # list of indices (key) and lengths (value)

# matrix ========

def build_matrix(rows, cols):
    """
    build matrix with random (non-zero) values
    :return: matrix: list
    """
    matrix = []
    for i in range(rows):
        col = bytearray([])  # mutable
        for j in range(cols):
            z = random.randint(1, 8849) # elevation in meters above mean sea level
            z2b = z.to_bytes(2, byteorder='big')
            col.append(z2b[0])  # high byte (big endian)
            col.append(z2b[1])  # low byte  (big endian)
        matrix.append(col)
    return matrix

# database ========

def build_db(connection):
    """
    build database
    :param connection: Connection
    :return: bool (success = True)
    """
    success = False
    try:
        sql = 'CREATE TABLE IF NOT EXISTS rows(id INTEGER PRIMARY KEY, len INTEGER NOT NULL, row BLOB NOT NULL);'
        connection.execute(sql)
        connection.commit()
        success = True
    except sqlite3.Error as bde:
        connection.rollback()
        print("SQLite build_db error: " + bde.args[0])
    finally:
        return success

def _get_row_len(idx):
    """
    get length of rows[idx] in bytes, before writing row to database.
    - new rows start with length 0.
    - after writing to database: use _set_row_len to update the length.
        based upon:   global var (self.)idx_len_list
        prerequisite: the indices start with 0, and increment += 1
    :param idx:
    :return: len: integer or None: error
    """
    global idx_len_list
    if len(idx_len_list)-1 != idx:
        print('Sequence is out of range, expected: '+str(len(idx_len_list)-1)+', got idx: '+str(idx))
        return None
    try:
        return idx_len_list[idx] # list element exists
    except IndexError:
        # new list element
        idx_len_list.append(0)
        return 0

def _set_row_len(idx, row_len):
    """
    set length of rows[idx] in bytes
    :param idx:
    :return: len: integer or None: error
    """
    try:
        idx_len_list[idx] = row_len
        return row_len
    except IndexError:
        print('Sequence is out of range, expected: 0..'+str(len(idx_len_list))+', got idx: '+str(idx))
        return None

def set_row(connection, idx, bytes, max_bytes):
    """
    insert row into table rows
    :param connection: Connection
    :param idx: integer
    :param bytes: bytearray
    :param max_bytes: integer
    :return: success: bool
    """
    success = False
    row_len = _get_row_len(idx)
    if row_len is None:
        return success
    bytes_len = len(bytes)
    try:
        if row_len == 0:
            # new row
            sql = 'INSERT INTO rows(id, len, row) VALUES(?, ?, zeroblob(?));'
            connection.execute(sql, (idx, bytes_len, max_bytes))
            # write blob contents
            with connection.blobopen("rows", "row", idx) as blob:
                blob.write(bytes)
            connection.commit()
            # set len in local list
            result = _set_row_len(idx, bytes_len)
            if result == bytes_len:
                success = True
        else:
            # append bytes to existing blob
            with connection.blobopen("rows", "row", idx) as blob:
                blob.seek(row_len) # set to absolute access position
                blob.write(bytes)
            connection.commit()
            new_len = row_len + bytes_len
            # set len in database
            sql = 'UPDATE rows SET len = ? WHERE id = ?;'
            curs = connection.cursor()
            curs.execute(sql, (new_len, idx))
            connection.commit()
            # set len in local list
            result = _set_row_len(idx, new_len)
            if result == new_len:
                success = True
        pass
    except sqlite3.Error as sre:
        connection.rollback()
        print("SQLite set_row error: " + sre.args[0])
    finally:
        return success

def get_row(cursor, idx):
    """
    get one row from the database
    :param cursor: Cursor
    :param idx: integer
    :return: row: tuple (id, length, bytearray), or None (error)
    """
    try:
        sql = "SELECT id, len, row FROM rows WHERE id=?;"
        cursor.execute(sql, (idx,))
        local_row = cursor.fetchone()
        bytes_len = local_row[1]
        return local_row[0], local_row[1], local_row[2][:bytes_len] # id, length, bytearray
    except sqlite3.Error as gre:
        print("SQLite get_row error: " + gre.args[0])
        return None # error

def run_main():
    # build matrix
    max_cols_in_row = 2*EDGE
    max_length = int(FACTOR * max_cols_in_row) # 2.4 * 2 * 1200 = 5760 bytes
    mtrx1 = build_matrix(EDGE, EDGE) # rows, cols
    # mtrx2 = build_matrix(EDGE, EDGE) # rows, cols
    try:
        # build connection to database
        db_filename = config("DB_FILENAME")
        print("DB filename: "+db_filename)
        if os.path.exists(db_filename):
            os.remove(db_filename)
        conn: Connection = sqlite3.connect(db_filename)
        curs: Cursor = conn.cursor()

        # build database
        done = build_db(conn)
        if not done:
            exit(1)

        # write first blob to database
        index = 0
        done = set_row(conn, index, mtrx1[index], max_length)
        if not done:
            exit(2)

        # write second blob to database
        done = set_row(conn, index, mtrx1[index+1], max_length)
        if not done:
            exit(2)

        # read first blob
        test_row = get_row(curs, index)
        if test_row is None:
            exit(3)
        if mtrx1[index]+mtrx1[index+1] == test_row[2]:
            print("Match in bytearrays in matrix1 and database.")
        else:
            print("Mismatch in bytearrays")
        pass
    except sqlite3.Error as e:
        print("SQLite main error: " + e.args[0])
        exit(4)
    pass

# main ========
run_main() # run main part of script
exit(0)    # successfully exit
