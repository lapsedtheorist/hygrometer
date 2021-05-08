#!/usr/bin/env python3
from inky import InkyPHAT
from PIL import Image, ImageFont, ImageDraw
from font_fredoka_one import FredokaOne
from am2320 import AM2320
import argparse
from datetime import datetime, timezone
import pytz
import math

parser = argparse.ArgumentParser(description='Sample the sensors of the Hygrometer and display them')
parser.add_argument('--i2c', type=int, default=1, choices=[0, 1], help='Which i2c bus to use (default: 1)')
args = parser.parse_args()

def date_suffixed(day):
    d = {"1":"st","2":"nd","3":"rd"}
    return (day if day[-2] != "0" else day[-1]) + ("th" if day[-2]=="1" else d.get(day[-1],"th"))

def sample_hygrometer(device):
    dt = datetime.now(tz=timezone.utc)
    (t,h) = device.readSensor()
    return (dt.isoformat(timespec='seconds'), t, h)

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
    smallFont = ImageFont.truetype("04B_03__.ttf", 8)
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

am2320 = AM2320(args.i2c)
(sensor_dt, sensor_t, sensor_h) = sample_hygrometer(am2320)

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
