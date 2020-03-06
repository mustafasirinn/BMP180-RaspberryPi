#!/usr/bin/python
# -*- coding: utf-8 -*-
import BMP180 as BMP180
from datetime import datetime

now = datetime.now()
current_time = now.strftime("%Y-%m-%d %H:%M:%S")

sensor = BMP180.BMP180()

print(str(current_time)+", {0:0.2f}".format(sensor.basinc_olc()))