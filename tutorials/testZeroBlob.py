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

# matrix ========

def build_matrix(m_rows, m_cols):
    """
    build matrix with random (non-zero) values
    :return: matrix: list
    """
    matrix = []
    for i in range(m_rows):
        col = bytearray([])  # mutable
        for j in range(m_cols):
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

def set_row(connection, srid, bytes, max_bytes):
    """
    insert row into table rows
    :param connection: Connection
    :param srid: integer
    :param bytes: bytearray
    :param max_bytes: integer
    :return: success: bool
    """
    success = False
    try:
        sql = 'INSERT INTO rows(id, len, row) VALUES(?, ?, zeroblob(?));'
        bytes_len = len(bytes)
        connection.execute(sql, (srid, bytes_len, max_bytes))
        # write blob contents
        with connection.blobopen("rows", "row", srid) as blob:
            blob.write(bytes)
        connection.commit()
        success = True
    except sqlite3.Error as sre:
        connection.rollback()
        print("SQLite set_row error: " + sre.args[0])
    finally:
        return success

def get_row(cursor, grid):
    """
    get one row from the database
    :param cursor: Cursor
    :param grid: integer
    :return: row: tuple (id, length, bytearray), or None (error)
    """
    try:
        sql = "SELECT id, len, row FROM rows WHERE id=?;"
        cursor.execute(sql, (grid,))
        local_row = cursor.fetchone()
        bytes_len = local_row[1]
        return local_row[0], local_row[1], local_row[2][:bytes_len] # id, length, bytearray
    except sqlite3.Error as gre:
        print("SQLite get_row error: " + gre.args[0])
        return None # error

# main ========

# build matrix
factor = 2.4
max_cols_in_row = 2*EDGE
max_length = factor * max_cols_in_row # 2.4 * 2 * 1200 = 5760 bytes
rows = EDGE
cols = EDGE
mtrx1 = build_matrix(rows, cols)
# mtrx2 = build_matrix(rows, cols)

try:
    # build empty database wit a blob
    db_filename = config("DB_FILENAME")
    print("DB filename: "+db_filename)
    if os.path.exists(db_filename):
        os.remove(db_filename)
    conn: Connection = sqlite3.connect(db_filename)
    curs: Cursor = conn.cursor()
    done = build_db(conn)
    if not done:
        exit(1)
    # write first blob to database
    idx = 0
    done = set_row(conn, idx, mtrx1[idx], max_length)
    if not done:
        exit(2)
    # read first blob
    row = get_row(curs, idx)
    if row is None:
        exit(3)
    if mtrx1[idx] == row[2]:
        print("Match in bytearrays in matrix1 and database.")
    else:
        print("Mismatch in bytearrays")
    pass
except sqlite3.Error as e:
    print("SQLite main error: " + e.args[0])
    exit(4)
pass
exit(0)
