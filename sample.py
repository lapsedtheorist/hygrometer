#!/usr/bin/env python3

from am2320 import AM2320
import argparse
from datetime import datetime, timezone
import json
import pathlib
import sqlite3

parser = argparse.ArgumentParser(description='Sample the sensors of the Hygrometer')
parser.add_argument('--i2c', type=int, default=1, choices=[0, 1], help='Which i2c bus to use (default: 1)')
parser.add_argument('--db', nargs='?', type=pathlib.Path, const='hygrometer.db', help='Use database filepath (default: hygrometer.db)')
args = parser.parse_args()

def open_timeseries_database_write(path):
    try:
        db_path = path.resolve(strict=True)
    except FileNotFoundError:
        sql3con = sqlite3.connect(path)
        sql3cur = sql3con.cursor()
        sql3cur.execute('CREATE TABLE timeseries (datetime text, temperature real, humidity real)')
        sql3cur.execute('CREATE UNIQUE INDEX datetime_idx ON timeseries (datetime DESC)')
        sql3con.commit()
    else:
        sql3con = sqlite3.connect(path)
        sql3cur = sql3con.cursor()
    return (sql3con, sql3cur)

def sample_hygrometer(device):
    dt = datetime.now(tz=timezone.utc)
    (t,h) = device.readSensor()
    return (dt.isoformat(timespec='seconds'), t, h)

def queue_hygrometer_sample(cursor, datetime, temperature, humidity):
    cursor.execute('INSERT INTO timeseries VALUES (?,?,?)', (datetime, temperature, humidity))

am2320 = AM2320(args.i2c)
(dt, t, h) = sample_hygrometer(am2320)

if args.db is not None:
    (sql3con, sql3cur) = open_timeseries_database_write(args.db)
    queue_hygrometer_sample(sql3cur, dt, t, h)
    sql3con.commit()
else:
    print(json.dumps({"datetime": dt, "temperature": t, "humidity": h}))
