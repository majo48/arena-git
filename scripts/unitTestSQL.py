#!/usr/bin/env python3

"""
    Unit test the SQL database with all test cases in
        SQL database > meta data > tileinfo > unittests (list)
"""

# packages ========

from decouple import config
from scripts.Dbsql import Dbsql
import json
from Dbcache import Dbcache

# functions ========

def get_test_cases(xdb_path):
    """
    get test cases from one or more metadata records
    :return: list of test cases
    """
    test_case_list = []  # list of test cases
    with Dbsql(xdb_path) as sqldb:
        metadatas = sqldb.get_metadata()
        for metadata in metadatas:
            mydict = json.loads(metadata[1])
            test_cases = mydict["unittests"]
            for test_case in test_cases:
                test_case_list.append(test_case)
            pass
        pass
    return test_case_list

# main code ========

xdb_path = config("DB_FILENAME")
test_case_list = get_test_cases(xdb_path)
#
passed = 0
failed = 0
with Dbcache(xdb_path) as dbcache:
    # run unit test cases against the cache and database
    for test_case in test_case_list:
        x = test_case["x"] # longitude
        y = test_case["y"] # latitude
        z = test_case["z"] # elevation in meters
        elev = dbcache.get_elevation(y,x)
        if elev == z:
            passed += 1 # same
        else:
            failed += 1 # different
            print("Failed: "+str(test_case))
        pass
    pass
pass
print("unitTestSQL: passed="+str(passed)+", failed="+str(failed))
if failed==0: print("SUCCESS")
else: print("FAILED")
exit(0)