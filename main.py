import time
import matplotlib.pyplot as plt
from roomba_interface import Roomba, RoombaMode

roomba = Roomba('COM4')
# roomba.reset()
roomba.setMode(RoombaMode.SAFE)
roomba.beginSensorLoop()
roomba.setDigitsASCII('help')

print(roomba.sensorData['enc-left'], roomba.sensorData['enc-right'])
roomba.driveVel(200, 200)
time.sleep(1)
roomba.driveVel(0, 0)
time.sleep(1)
print(roomba.sensorData['enc-left'], roomba.sensorData['enc-right'])
roomba.driveVel(-100, -100)
time.sleep(2)
roomba.driveVel(0, 0)
time.sleep(1)
print(roomba.sensorData['enc-left'], roomba.sensorData['enc-right'])


roomba.close()
plt.plot(roomba.encoderData)
plt.show()