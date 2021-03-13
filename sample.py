#!/usr/bin/env python3

from am2320 import AM2320
from datetime import datetime, timezone

# For a Raspberry Pi Zero, the i2c bus will be 0 or 1
I2C_BUS = 0

am2320 = AM2320(I2C_BUS)
dt = datetime.now(tz=timezone.utc)
(t,h) = am2320.readSensor()
print(dt.isoformat(timespec='seconds'), t, h)
