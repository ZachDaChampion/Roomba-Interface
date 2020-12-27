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
roomba.driveVel(-200, -200)
time.sleep(1)
roomba.driveVel(0, 0)
time.sleep(1)


roomba.close()
data = pd.DataFrame(roomba.sensorData.history)
plt.figure(1)
plt.subplot(211)
plt.plot(data['enc-left'])
plt.plot(data['enc-right'])
plt.subplot(212)
plt.plot(data['vel-left'])
plt.plot(data['vel-right'])
plt.show()
