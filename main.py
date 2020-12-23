import time
from roomba_interface import Roomba, RoombaMode

roomba = Roomba('COM4')
roomba.setMode(RoombaMode.SAFE)
roomba.setDigitsASCII('help')

time.sleep(5)

del roomba
