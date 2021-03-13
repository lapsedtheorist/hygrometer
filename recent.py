#!/usr/bin/env python3

from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3

def open_timeseries_database_read(path='hygrometer.db'):
    try:
        db_path = Path(path).resolve(strict=True)
    except FileNotFoundError:
        print('ERROR: database {} not found'.format(path))
    else:
        sql3con = sqlite3.connect(path)
        sql3cur = sql3con.cursor()
    return (sql3con, sql3cur)

def read_hygrometer(cursor):
    cursor.execute('SELECT * FROM timeseries ORDER BY datetime LIMIT 300')
    return cursor.fetchall()

(sql3con, sql3cur) = open_timeseries_database_read()
data = read_hygrometer(sql3cur)
keys = ("datetime", "temperature", "humidity")
results = [dict(zip(keys, values)) for values in data]

print(json.dumps(results))
