#!/usr/bin/env python3

"""
    Test Python Pickle
"""

import os
import sys
import pickle # automatically calls cPickle in Python 3.5+ 
import sqlite3

DBNAME = 'pickle.db'

def buildDatabase():
    try:
        sqliteConnection = sqlite3.connect(DBNAME)
        cursor = sqliteConnection.cursor()
        sql = """ 
            CREATE TABLE IF NOT EXISTS metaData(
                id INTEGER PRIMARY KEY,
                pData BLOB NOT NULL
        );    """

        cursor.execute(sql)
        sqliteConnection.commit()
        cursor.close()

    except sqlite3.Error as error:
        print("Failed to build database.", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()

def insertBLOB(id, pData):
    try:
        sqliteConnection = sqlite3.connect(DBNAME)
        cursor = sqliteConnection.cursor()
        sql = """ INSERT INTO metaData(id, pData) VALUES (?, ?)"""

        cursor.execute(sql, (id, pData))
        sqliteConnection.commit()
        cursor.close()

    except sqlite3.Error as error:
        print("Failed to insert blob data into sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()

def readBLOB(id):
    try:
        sqliteConnection = sqlite3.connect(DBNAME)
        cursor = sqliteConnection.cursor()
        sql = """ SELECT pData FROM metaData WHERE id=?; """

        cursor.execute(sql, (id,))
        sqliteConnection.commit()
        rslt = cursor.fetchone()[0]
        cursor.close()

    except sqlite3.Error as error:
        print("Failed to insert blob data into sqlite table", error)
        rslt = None
    finally:
        if sqliteConnection:
            sqliteConnection.close()
        return rslt



# just pickle ========
oldList = [ 10, 12, 13, 15, 20, 30, 33, 43, 50, 77, 81, 82, 83, 99, 100 ]
print(oldList)
pData = pickle.dumps(oldList, protocol=-1)
unpickled1 = pickle.loads(pData)
print(unpickled1)

# with SQLite3 ========
if os.path.exists(DBNAME):
    os.remove(DBNAME)

# build a new db for each session 
buildDatabase() 

# insert binary data
insertBLOB(1, pData) 

# unpickle value from db
unpickled2 = pickle.loads(readBLOB(1))
print(unpickled2)

pass