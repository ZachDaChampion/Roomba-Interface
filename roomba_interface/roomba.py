import serial
import struct
import time
from typing import List
from enum import Enum


class RoombaMode(Enum):
  PASSIVE = 0
  SAFE = 1
  FULL = 2


class Roomba:

  def __init__(self, _port: str):
    self.mode = RoombaMode.PASSIVE
    self.connection = serial.Serial(_port, 115200, bytesize=serial.EIGHTBITS,
                                    parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
    self.connection.write(struct.pack('>B', 128))

  # set the mode of the roomba
  def setMode(self, _mode: RoombaMode):
    if self.mode == _mode or _mode == RoombaMode.PASSIVE:
      return
    if _mode == RoombaMode.SAFE:
      self.connection.write(struct.pack('>B', 131))
      time.sleep(.02)
    elif _mode == RoombaMode.FULL:
      self.connection.write(struct.pack('>B', 132))
      time.sleep(.02)

  # drive the roomba using integrated velocity controllers
  # each wheel is controlled independently
  # velocity range is -500 to 500 mm/sec
  # integrated controller works in steps of 28.5 mm/sec
  def driveVel(self, _right: int, _left: int):
    if self.mode == RoombaMode.PASSIVE:
      print('instruction cannot be carried out because Roobma is in PASSIVE mode')
      return
    self.connection.write(struct.pack('>Bhh', 145, _right, _left))

  # drive the roomba using PWM
  # each wheel is controlled independently
  # PWM range is -255 to 255
  def drivePWM(self, _right: int, _left: int):
    if self.mode == RoombaMode.PASSIVE:
      print('instruction cannot be carried out because Roobma is in PASSIVE mode')
      return
    self.connection.write(struct.pack('>Bhh', 146, _right, _left))

  # set the LEDs on the roomba
  # power color ranges from 0 to 255, where 0 is green and 255 is red
  # power intensity ranges from 0 to 255, where 0 is off and 255 is max
  def setLEDs(self, _check_led: bool, _debris_led: bool, _spot_led: bool, _power_color: int, _power_intensity: int):
    self.connection.write(struct.pack(
        '>BBBB', generateByte([_check_led, 0, _spot_led, _debris_led]), _power_color, _power_intensity))

  # set the raw segments of the 7-segment display
  # digits on roomba are 3, 2, 1, 0 from left to right
  # see spec for segment labels because i dont feel like typing it all out here
  def setDigitsRaw(self, _3: int, _2: int, _1: int, _0: int):
    self.connection.write(struct.pack('>BBBBB', 163, _3, _2, _1, _0))

  # set the segments of the 7-segment display to an ascii character
  # digits on roomba are 3, 2, 1, 0 from left to right
  # see spec for supported characters because i dont feel like typing it all out here
  def setDigitsASCII(self, _3: str, _2: str, _1: str, _0: str):
    if _3 not in _ascii_digits.keys() or _2 not in _ascii_digits.keys() or _1 not in _ascii_digits.keys() or _0 not in _ascii_digits.keys():
      print('one or more of your digits cannot be displayed')
      return
    self.connection.write(struct.pack(
        '>BBBBB', 164, _ascii_digits[_3], _ascii_digits[_2], _ascii_digits[_1], _ascii_digits[_0]))


# generate a byte from a list of booleans
def generateByte(bits: List[bool], size=8):
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
