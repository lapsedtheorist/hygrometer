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

def read_hygrometer(limit):
    (sql3con, sql3cur) = open_timeseries_database_read(args.db)
    sql3cur.execute('SELECT * FROM timeseries ORDER BY datetime DESC LIMIT :limit', {"limit": limit})
    data = sql3cur.fetchall()
    sql3con.close()
    return data

def recent_data(env, start_response):
    data = read_hygrometer(limit=300)
    keys = ("datetime", "temperature", "humidity")
    results = [dict(zip(keys, values)) for values in data]
    start_response('200 OK', [('Content-Type','application/json; charset=utf-8')])
    return [str.encode(json.dumps(results))]

def application(env, start_response):
    data = read_hygrometer(limit=1)
    keys = ("datetime", "temperature", "humidity")
    results = [dict(zip(keys, values)) for values in data]
    start_response('200 OK', [('Content-Type','application/json; charset=utf-8')])
    return [str.encode(json.dumps(results[0]))]

