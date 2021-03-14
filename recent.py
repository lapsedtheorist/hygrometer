#!/usr/bin/env python3

import argparse
from datetime import datetime, timezone
import json
import pathlib
import sqlite3

parser = argparse.ArgumentParser(description='Sample the sensors of the Hygrometer')
parser.add_argument('--db', type=pathlib.Path, default='hygrometer.db', help='Use database filepath (default: hygrometer.db)')
args = parser.parse_args()

def open_timeseries_database_read(path):
    try:
        db_path = path.resolve(strict=True)
    except FileNotFoundError:
        print('ERROR: database {} not found'.format(path))
        exit()
    else:
        sql3con = sqlite3.connect(path)
        sql3cur = sql3con.cursor()
    return (sql3con, sql3cur)

def read_hygrometer(cursor):
    cursor.execute('SELECT * FROM timeseries ORDER BY datetime LIMIT 300')
    return cursor.fetchall()

(sql3con, sql3cur) = open_timeseries_database_read(args.db)
data = read_hygrometer(sql3cur)
keys = ("datetime", "temperature", "humidity")
results = [dict(zip(keys, values)) for values in data]

print(json.dumps(results))
