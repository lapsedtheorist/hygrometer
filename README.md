Temperature and Humidity sampling with a Raspberry Pi Zero
==========================================================

This set of scripts is what I'm using to sample temperature and humidity from
an [AM2320
sensor](https://shop.pimoroni.com/products/digital-temperature-and-humidity-sensor)
running on a [Raspberry Pi Zero
W](https://shop.pimoroni.com/products/raspberry-pi-zero-w).

A crontab runs `hygrometer/sample.py` every whenever, which populates the data
into the database `hygrometer.db` which is then read by `hygrometer/recent.py`
as appropriate.
