#!/usr/bin/python
# -*- coding: utf-8 -*-
import BMP180 as BMP180
import datetime    
import time
import os.path

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

baslamadi = True

def upload(dosya):
    file2 = drive.CreateFile()
    file2.SetContentFile(dosya)
    file2.Upload()

while(1):
    now = datetime.datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    saatlik_dosya = now.strftime("%d%m%Y_%H00.txt")
    sensor = BMP180.BMP180()
    print (str(current_time)+", {0:0.2f}".format(sensor.basinc_olc())+"\n")
    if os.path.exists(saatlik_dosya):
        pass
    elif baslamadi:
        baslamadi = False
        pass
    else:
        d2 = datetime.datetime.now() - datetime.timedelta(hours=1)
        upload(d2.strftime("%d%m%Y_%H00.txt"))    
    f = open(saatlik_dosya,'a')
    f.write(str(current_time)+", {0:0.2f}".format(sensor.basinc_olc())+"\n")
    f.close()
    time.sleep(1)