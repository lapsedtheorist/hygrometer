#!/usr/bin/env python3

import argparse
from datetime import datetime, timezone
import json
import pathlib
import sqlite3
import uwsgi

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
    keys = ("datetime", "temperature", "humidity")
    results = [dict(zip(keys, values)) for values in data]
    return results

def recent_data():
    data = read_hygrometer(limit=10)
    return data

def last_data():
    data = read_hygrometer(limit=1)
    return data[0]

def application(env, start_response):
    p = env['PATH_INFO']
    if p == "/data":
        body = last_data()
        start_response('200 OK', [('Content-Type', 'application/json; charset=utf-8')])
        return [str.encode(json.dumps(body))]
    elif p == "/recent":
        body = recent_data()
        start_response('200 OK', [('Content-Type', 'application/json; charset=utf-8')])
        return [str.encode(json.dumps(body))]
    else:
        body = {"error": "Request path not recognised"}
        start_response('404 Not Found', [('Content-Type', 'application/json; charset=utf-8')])
        return [str.encode(json.dumps(body))]
