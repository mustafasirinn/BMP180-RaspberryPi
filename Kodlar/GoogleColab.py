import matplotlib.pyplot as plt
import os
from pathlib import Path
from datetime import datetime
import matplotlib.dates as mdates
x = []
y = []

dosyalar = []

path = "/content/drive/My Drive/"
entries = Path(path)
for entry in entries.iterdir():
    if (entry.name[-3:]  == "txt"):
       dosyalar.append(path+entry.name)
       print(path+entry.name)
for dosya in dosyalar:
  with open(dosya, "r") as fp:
    for line in fp:
          str = line
          array = str.split(", ")
          x.append(datetime.strptime(array[0], "%Y-%m-%d %H:%M:%S"))
          y.append(int(array[1][:-4]))
fig,ax1 = plt.subplots()
plt.plot(x,y)
monthyearFmt = mdates.DateFormatter('%Y-%m-%d %H:%M:%S')
ax1.xaxis.set_major_formatter(monthyearFmt)
_ = plt.xticks(rotation=90) 
