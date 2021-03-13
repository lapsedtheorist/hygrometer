#!/usr/bin/env python3

from am2320 import AM2320
from datetime import datetime, timezone
from pathlib import Path
import sqlite3

# For a Raspberry Pi Zero, the i2c bus will be 0 or 1
I2C_BUS = 0

def open_timeseries_database_write(path='hygrometer.db'):
    try:
        db_path = Path(path).resolve(strict=True)
    except FileNotFoundError:
        sql3con = sqlite3.connect(path)
        sql3cur = sql3con.cursor()
        sql3cur.execute('CREATE TABLE timeseries (datetime text, temperature real, humidity real)')
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

am2320 = AM2320(I2C_BUS)
(dt, t, h) = sample_hygrometer(am2320)

(sql3con, sql3cur) = open_timeseries_database_write()
queue_hygrometer_sample(sql3cur, dt, t, h)
sql3con.commit()
