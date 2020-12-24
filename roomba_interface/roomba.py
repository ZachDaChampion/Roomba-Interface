import serial
import struct
import time
import threading
import sys
from typing import List
from enum import Enum


class RoombaMode(Enum):
  PASSIVE = 0
  SAFE = 1
  FULL = 2


class Roomba:

  connection = None
  mode = RoombaMode.PASSIVE
  encoderData = []
  sensorData = {
      'updated': 0,
      'battery-charge': 0,
      'enc-right': 0,
      'enc-right-raw': 0,
      'enc-right-offset': 0,
      'enc-left': 0,
      'enc-left-raw': 0,
      'enc-left-offset': 0
  }
  _sensorThread = None
  _sensorThreadExit = False

  def __init__(self, _port: str):
    self.mode = RoombaMode.PASSIVE
    self.connection = serial.Serial(_port, 115200, write_timeout=0)
    if (self.connection.is_open):
      self.connection.close()
    self.connection.open()
    time.sleep(1)
    print('Connected to serial port')
    self.connection.write(struct.pack('>B', 128))
    time.sleep(.5)
    print('Started Roomba OI')

  def close(self):
    if self.connection is not None:
      if self._sensorThread is not None:
        self._sensorThreadExit = True
        self._sensorThread.join()
      self.connection.write(struct.pack('>B', 173))
      time.sleep(1)
      self.connection.close()
    print('Serial connection terminated')

  # reset the roomba as if the battery was removed
  def reset(self):
    if self.connection is None:
      print('connection to Roomba was not initialized')
      return
    self.connection.write(struct.pack('>B', 7))
    print('Reset Roomba')
    time.sleep(10)
    self.connection.write(struct.pack('>B', 128))
    time.sleep(.5)
    print('Restarted Roomba OI')

  # set the mode of the roomba
  def setMode(self, _mode: RoombaMode):
    if self.connection is None:
      print('connection to Roomba was not initialized')
      return
    if self.mode == _mode or _mode == RoombaMode.PASSIVE:
      print("Roomba mode was not changed")
      return
    if _mode == RoombaMode.SAFE:
      self.connection.write(struct.pack('>B', 131))
      time.sleep(.02)
      self.mode = RoombaMode.SAFE
    elif _mode == RoombaMode.FULL:
      self.connection.write(struct.pack('>B', 132))
      time.sleep(.02)
      self.mode = RoombaMode.FULL
    print("Roomba mode changed")

  # drive the roomba using integrated velocity controllers
  # each wheel is controlled independently
  # velocity range is -500 to 500 mm/sec
  # integrated controller works in steps of 28.5 mm/sec
  def driveVel(self, _right: int, _left: int):
    if self.connection is None:
      print('connection to Roomba was not initialized')
      return
    if self.mode == RoombaMode.PASSIVE:
      print('instruction cannot be carried out because Roobma is in PASSIVE mode')
      return
    self.connection.write(struct.pack('>Bhh', 145, _right, _left))

  # drive the roomba using PWM
  # each wheel is controlled independently
  # PWM range is -255 to 255
  def drivePWM(self, _right: int, _left: int):
    if self.connection is None:
      print('connection to Roomba was not initialized')
      return
    if self.mode == RoombaMode.PASSIVE:
      print('instruction cannot be carried out because Roobma is in PASSIVE mode')
      return
    self.connection.write(struct.pack('>Bhh', 146, _right, _left))

  # set the LEDs on the roomba
  # power color ranges from 0 to 127, where 0 is green and 127 is red
  # power intensity ranges from 0 to 255, where 0 is off and 127 is max
  def setLEDs(self, _check_led: bool, _debris_led: bool, _spot_led: bool, _power_color: int, _power_intensity: int):
    if self.connection is None:
      print('connection to Roomba was not initialized')
      return
    if self.mode == RoombaMode.PASSIVE:
      print('instruction cannot be carried out because Roobma is in PASSIVE mode')
      return
    self.connection.write(struct.pack(
        '>BBBB', 139, generateByte([_check_led, 0, _spot_led, _debris_led]), _power_color, _power_intensity))

  # set the raw segments of the 7-segment display
  # digits on roomba are 3, 2, 1, 0 from left to right
  # see spec for segment labels because i dont feel like typing it all out here
  def setDigitsRaw(self, _3: int, _2: int, _1: int, _0: int):
    if self.connection is None:
      print('connection to Roomba was not initialized')
      return
    if self.mode == RoombaMode.PASSIVE:
      print('instruction cannot be carried out because Roobma is in PASSIVE mode')
      return
    self.connection.write(struct.pack('>BBBBB', 163, _3, _2, _1, _0))

  # set the segments of the 7-segment display to an ascii character
  # message must be exactly four characters
  # see spec for supported characters because i dont feel like typing it all out here
  def setDigitsASCII(self, _msg: str):
    if self.connection is None:
      print('connection to Roomba was not initialized')
      return
    if self.mode == RoombaMode.PASSIVE:
      print('instruction cannot be carried out because Roobma is in PASSIVE mode')
      return
    if len(_msg) != 4 or _msg[0] not in _ascii_digits.keys() or _msg[1] not in _ascii_digits.keys() or _msg[2] not in _ascii_digits.keys() or _msg[3] not in _ascii_digits.keys():
      print('one or more of your digits cannot be displayed')
      return
    self.connection.write(struct.pack(
        '>BBBBB', 164, _ascii_digits[_msg[0]], _ascii_digits[_msg[1]], _ascii_digits[_msg[2]], _ascii_digits[_msg[3]]))

  # update all of the appropriate sensor data
  def updateSensors(self):
    if self.connection is None:
      print('connection to Roomba was not initialized')
    updatedAt = int(time.time() * 1000)
    if (updatedAt - self.sensorData['updated'] < 15):
      print('Sensor data not yet updated by Roomba')
      return
    self.connection.write(struct.pack(
        '>BBBBBB', 149, 4, 25, 26, 43, 44))
    raw_data = struct.unpack('HHhh', self.connection.read(8))
    self.sensorData['updated'] = updatedAt
    self.sensorData['battery-charge'] = raw_data[0] / raw_data[1]
    if self.sensorData['enc-right-raw'] > 30000 and raw_data[2] < -30000:
      self.sensorData['enc-right-offset'] += 65535
      print('Overflow')
    elif self.sensorData['enc-right-raw'] < -30000 and raw_data[2] > 30000:
      self.sensorData['enc-right-offset'] -= 65535
      print('Overflow')
    self.sensorData['enc-right-raw'] = raw_data[2]
    self.sensorData['enc-right'] = self.sensorData['enc-right-raw'] + \
        self.sensorData['enc-right-offset']
    if self.sensorData['enc-left-raw'] > 30000 and raw_data[3] < -30000:
      self.sensorData['enc-left-offset'] += 65535
      print('Overflow')
    elif self.sensorData['enc-left-raw'] < -30000 and raw_data[3] > 30000:
      self.sensorData['enc-left-offset'] -= 65535
      print('Overflow')
    self.sensorData['enc-left-raw'] = raw_data[3]
    self.sensorData['enc-left'] = self.sensorData['enc-left-raw'] + \
        self.sensorData['enc-left-offset']

    self.encoderData.append(
        (self.sensorData['enc-left'], self.sensorData['enc-right']))

  # begin sensor update loop in separate thread
  def beginSensorLoop(self):
    self._sensorThreadExit = False
    self._sensorThread = threading.Thread(target=self.sensorLoop, daemon=True)
    self._sensorThread.start()
    time.sleep(.03)

  # update sensors periodically
  def sensorLoop(self, rate: int = 15):
    while (not self._sensorThreadExit):
      self.updateSensors()
      time.sleep(.03)
    print('Thread exited')


# generate a byte from a list of booleans
def generateByte(bits: List[bool], size: int = 8):
  p = bits[-size:]
  return sum(v << i for i, v in enumerate(p[::-1]))


_ascii_digits = {
    ' ': 32,
    '!': 33,
    '"': 34,
    '#': 35,
    '%': 37,
    '&': 38,
    "'": 39,
    ',': 44,
    '-': 45,
    '.': 46,
    '/': 47,
    '0': 48,
    '1': 49,
    '2': 50,
    '3': 51,
    '4': 52,
    '5': 53,
    '6': 54,
    '7': 55,
    '8': 56,
    '9': 57,
    ':': 58,
    ';': 59,
    '=': 61,
    '?': 63,
    'a': 65,
    'b': 66,
    'c': 67,
    'd': 68,
    'e': 69,
    'f': 70,
    'g': 71,
    'h': 72,
    'i': 73,
    'j': 74,
    'k': 75,
    'l': 76,
    'm': 77,
    'n': 78,
    'o': 79,
    'p': 80,
    'q': 81,
    'r': 82,
    's': 83,
    't': 84,
    'u': 85,
    'v': 86,
    'w': 87,
    'x': 88,
    'y': 89,
    'z': 90,
    '[': 91,
    '\\': 92,
    ']': 93,
    '^': 94,
    '_': 95,
    '`': 96,
    '{': 123,
    '}': 125,
    '~': 126
}
