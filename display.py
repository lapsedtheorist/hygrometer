#!/usr/bin/env python3
from inky import InkyPHAT
from PIL import Image, ImageFont, ImageDraw
from font_fredoka_one import FredokaOne
import argparse
from datetime import datetime, timezone
import pytz
import math
import pathlib
import sqlite3

parser = argparse.ArgumentParser(description='Read the last readings of the Hygrometer and display them')
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

def last_data():
    data = read_hygrometer(limit=1)
    return data[0]

def date_suffixed(day):
    d = {"1":"st","2":"nd","3":"rd"}
    return (day if day[-2] != "0" else day[-1]) + ("th" if day[-2]=="1" else d.get(day[-1],"th"))

def render_datetime(sensor_dt):
    img = Image.new("P", (phat.HEIGHT, phat.WIDTH))
    draw = ImageDraw.Draw(img)
    mediumFont = ImageFont.truetype(FredokaOne, 16)
    largeFont = ImageFont.truetype(FredokaOne, 32)
    dt = datetime.fromisoformat(sensor_dt).astimezone(pytz.timezone("Europe/London"))
    day = dt.strftime("%A")
    (day_w, day_h) = mediumFont.getsize(day)
    date = "{}".format(date_suffixed(dt.strftime("%d")))
    (date_w, date_h) = mediumFont.getsize(date)
    space = math.floor(day_h * 0.75)
    time = dt.strftime("%H:%M")
    (time_w, time_h) = largeFont.getsize(time)
    draw.text((0, 0), day, phat.BLACK, mediumFont)
    draw.text((0, day_h), date, phat.BLACK, mediumFont)
    draw.text((0, day_h + date_h + space), time, phat.BLACK, largeFont)
    return img.crop((0, 0, max(day_w, date_w, time_w), day_h + date_h + space + time_h)).rotate(90, expand=True)

def render_sensor_data(data_type, sensor_value):
    img = Image.new("P", (phat.HEIGHT, math.floor(phat.WIDTH/3)))
    draw = ImageDraw.Draw(img)
    local_dir = pathlib.Path(__file__).parent.absolute()
    smallFont = ImageFont.truetype("{}/04B_03__.ttf".format(local_dir), 8)
    largeFont = ImageFont.truetype(FredokaOne, 32)
    label = data_type.upper()
    if data_type == "temperature":
        text = "{}˚C".format(sensor_value)
    elif data_type == "humidity":
        text = "{}%".format(sensor_value)
    else:
        text = "?"
    (lw, lh) = smallFont.getsize(label)
    (tw, th) = largeFont.getsize(text)
    draw.text((0, 0), label, phat.RED, smallFont)
    draw.text((0, lh), text, phat.RED, largeFont)
    return img.crop((0, 0, max(lw, tw), lh+th)).rotate(90, expand=True)

# update the display during normal waking hours (roughly)
now = datetime.now(tz=timezone.utc).astimezone(pytz.timezone("Europe/London"))
if now.hour >= 7 and (now.hour < 22 or (now.hour == 22 and now.minute == 0)):
    data = last_data()
    sensor_dt = data["datetime"]
    sensor_t = data["temperature"]
    sensor_h = data["humidity"]

    phat = InkyPHAT("red")
    phat.set_border(phat.WHITE)
    #phat.h_flip = True
    #phat.v_flip = True

    img_dt = render_datetime(sensor_dt)
    img_t = render_sensor_data("temperature", sensor_t)
    img_h = render_sensor_data("humidity", sensor_h)

    canvas = Image.new("P", (phat.WIDTH, phat.HEIGHT))
    canvas.paste(img_dt, box=(3, phat.HEIGHT - img_dt.height - 3))
    canvas.paste(img_t, box=(phat.WIDTH - img_t.width - 12 - img_h.width, phat.HEIGHT - img_t.height - 3))
    canvas.paste(img_h, box=(phat.WIDTH - img_h.width - 3, phat.HEIGHT - img_h.height - 3))

    phat.set_image(canvas)
    phat.show()
