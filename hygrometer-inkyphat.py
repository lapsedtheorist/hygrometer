#!/usr/bin/env python3
from inky import InkyPHAT
from PIL import Image, ImageFont, ImageDraw
from font_fredoka_one import FredokaOne
from am2320 import AM2320
import argparse
from datetime import datetime, timezone
import pytz

parser = argparse.ArgumentParser(description='Sample the sensors of the Hygrometer and display them')
parser.add_argument('--i2c', type=int, default=1, choices=[0, 1], help='Which i2c bus to use (default: 1)')
args = parser.parse_args()

def date_suffixed(day):
    d = {"1":"st","2":"nd","3":"rd"}
    return (day if day[-2] != "0" else day[-1]) + ("th" if day[-2]=="1" else d.get(day[-1],"th"))

def format_datetime(dt):
    dto = datetime.fromisoformat(dt).astimezone(pytz.timezone("Europe/London"))
    return dto.strftime("%A {}, %H:%M".format(date_suffixed(dto.strftime("%d"))))

def format_temperature(t):
    return "{}˚C".format(t)

def format_humidity(h):
    return "{}%".format(h)

def sample_hygrometer(device):
    dt = datetime.now(tz=timezone.utc)
    (t,h) = device.readSensor()
    return (dt.isoformat(timespec='seconds'), t, h)

phat = InkyPHAT("red")
phat.set_border(phat.WHITE)
phat.h_flip = True
phat.v_flip = True

img = Image.new("P", (phat.WIDTH, phat.HEIGHT))
draw = ImageDraw.Draw(img)

smallFont = ImageFont.truetype("04B_03__.ttf", 8)
mediumFont = ImageFont.truetype(FredokaOne, 16)
largeFont = ImageFont.truetype(FredokaOne, 32)

am2320 = AM2320(args.i2c)
(sensor_dt, sensor_t, sensor_h) = sample_hygrometer(am2320)

dt = format_datetime(sensor_dt)
t = format_temperature(sensor_t)
h = format_humidity(sensor_h)

draw.text((5, 5), dt, phat.BLACK, mediumFont)

_tw, th = largeFont.getsize(t)
hw, hh = largeFont.getsize(h)
sh = max(th, hh)
sample_offset_x = phat.WIDTH - 5 - hw
sample_offset_y = phat.HEIGHT - 5 - sh

t_label = "TEMPERATURE"
lw, lh = smallFont.getsize(t_label)
label_offset_y = sample_offset_y - lh
draw.text((5, label_offset_y), t_label, phat.RED, smallFont)
draw.text((5, sample_offset_y), t, phat.RED, largeFont)

h_label = "HUMIDITY"
draw.text((sample_offset_x, label_offset_y), h_label, phat.RED, smallFont)
draw.text((sample_offset_x, sample_offset_y), h, phat.RED, largeFont)

phat.set_image(img)
phat.show()
