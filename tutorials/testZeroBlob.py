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
            z = random.randint(0, 8849) # elevation in meters above mean sea level
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

def set_row(connection, idx, bytes, offset, max_bytes):
    """
    insert row of bytes into table rows[idx]
    """
    success = False
    bytes_len = len(bytes)
    try:
        if offset == 0:
            # new row with max size blob of zeros
            sql = 'INSERT INTO rows(id, len, row) VALUES(?, ?, zeroblob(?));'
            connection.execute(sql, (idx, bytes_len, max_bytes))
            # write blob contents
            with connection.blobopen("rows", "row", idx) as blob:
                blob.write(bytes) # write blob to database
            connection.commit()
            success = True
        else:
            # offset >0: append bytes to existing blob
            with connection.blobopen("rows", "row", idx) as blob:
                blob.seek(offset) # set to absolute access position
                blob.write(bytes) # write blob to database
            connection.commit()
            # set len in database
            sql = 'UPDATE rows SET len = ? WHERE id = ?;'
            curs = connection.cursor()
            curs.execute(sql, (offset+bytes_len, idx))
            connection.commit()
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
    mtrx2 = build_matrix(EDGE, EDGE) # rows, cols
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

        # write first matrix blobs to database
        offset = 0
        for index in range(0,EDGE):
            done = set_row(conn, index, mtrx1[index], offset, max_length)
            if not done:
                exit(2)

        # append second matrix blobs to database: DB.rows[idx] = mtrx1[idx] + mtrx[idx]
        offset = len(mtrx1[0])
        for index in range(0, EDGE):
            done = set_row(conn, index, mtrx2[index], offset, max_length)
            if not done:
                exit(3)

        # read blobs from database and compare with matrices
        test_ok = 0
        test_nok = 0
        for index in range(0, EDGE):
            test_row = get_row(curs, index)
            if test_row is None:
                exit(4)
            if mtrx1[index]+mtrx2[index] == test_row[2]:
                test_ok += 1
            else:
                test_nok += 1
        print("Test OK: "+str(test_ok))
        print("Test not OK: "+str(test_nok))
        pass
    except sqlite3.Error as e:
        print("SQLite main error: " + e.args[0])
        exit(4)
    pass

# main ========
run_main() # run main part of script
exit(0)    # successfully exit
