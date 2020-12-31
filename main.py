import time
import pandas as pd
import matplotlib.pyplot as plt
from roomba_interface import Roomba, RoombaMode

roomba = Roomba('COM4', vel_filter_strength=.1)
roomba.setMode(RoombaMode.SAFE)
roomba.beginUpdateLoop()
roomba.setDigitsASCII('help')

roomba.driveVel(200, 200)
time.sleep(1)
roomba.driveVel(0, 0)
time.sleep(1)
roomba.driveVel(200, -200)
time.sleep(.9)
roomba.driveVel(0, 0)
time.sleep(1)
roomba.driveVel(200, 200)
time.sleep(1)
roomba.driveVel(0, 0)
time.sleep(1)
roomba.driveVel(200, -200)
time.sleep(.9)
roomba.driveVel(0, 0)
time.sleep(1)
roomba.driveVel(200, 200)
time.sleep(1)
roomba.driveVel(0, 0)
time.sleep(.1)


roomba.close()
data = roomba.history

plt.figure(1)
plt.subplot(211)
plt.title('Encoder ticks')
plt.plot(data['enc-left'])
plt.plot(data['enc-right'])
plt.subplot(212)
plt.title('Motor velocity')
plt.plot(data['vel-left'])
plt.plot(data['vel-right'])

plt.figure(2)
plt.subplot(221)
plt.title('Position')
plt.plot(data['x'], data['y'])
plt.subplot(222)
plt.title('Angle')
plt.plot(data['angle'])
plt.subplot(223)
plt.title('X')
plt.plot(data['x'])
plt.subplot(224)
plt.title('Y')
plt.plot(data['y'])

plt.show()
