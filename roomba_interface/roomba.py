import serial
import struct
import time
import threading
import sys
from enum import Enum
from typing import List
from . import command_data as cmd


class RoombaMode(Enum):
  OFF = 0
  PASSIVE = 1
  SAFE = 2
  FULL = 3


class SensorData:
  update_time = -1
  battery_charge = 0
  enc_left = 0
  enc_right = 0
  vel_left = 0
  vel_right = 0
  history = []

  def __init__(self, update_time, battery_charge, enc_left, enc_right, vel_left, vel_right):
    self.newData(update_time, battery_charge, enc_left,
                 enc_right, vel_left, vel_right)

  def newData(self, update_time, battery_charge, enc_left, enc_right, vel_left, vel_right):
    if (update_time != -1):
      self.history.append({'time': self.update_time, 'enc-left': self.enc_left, 'enc-right': self.enc_right,
                           'vel-left':  self.vel_left, 'vel-right': self.vel_right})
    self.update_time = update_time
    self.battery_charge = battery_charge
    self.enc_left = enc_left
    self.enc_right = enc_right
    self.vel_left = vel_left
    self.vel_right = vel_right


class Roomba:
  connection = None
  mode = RoombaMode.OFF
  sensorData = SensorData(0, 0, 0, 0, 0, 0)
  _vel_filter_str = .5
  _afterSensorsUpdate = []
  _updateThread = None
  _updateThreadExit = False
  _prevEncLeft = 0
  _prevEncRight = 0
  _prevVelLeft = 0
  _prevVelRight = 0
  _prevPrevVelLeft = 0
  _prevPrevVelRight = 0

  def __init__(self, port: str, vel_filter_strength: float = .5):
    self.connection = serial.Serial(port, 115200, write_timeout=0)
    self._vel_filter_str = vel_filter_strength
    if (self.connection.is_open):
      self.connection.close()
    self.connection.open()
    time.sleep(1)
    print('Connected to serial port')
    self.connection.write(struct.pack('>B', 128))
    time.sleep(.5)
    self.mode = RoombaMode.PASSIVE
    print('Started Roomba OI')

  def __del__(self):
    self.close()

  def close(self):
    if self.connection is not None and self.connection.is_open:
      if self._updateThread is not None:
        self._updateThreadExit = True
        self._updateThread.join()
      self.connection.write(struct.pack('>BB', 150, 0))
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
    self.mode = RoombaMode.OFF
    print('Reset Roomba')
    time.sleep(10)
    self.connection.write(struct.pack('>B', 128))
    time.sleep(.5)
    self.mode = RoombaMode.PASSIVE
    print('Restarted Roomba OI')

  # set the mode of the roomba
  def setMode(self, mode: RoombaMode):
    if self.connection is None:
      print('connection to Roomba was not initialized')
      return
    if self.mode == mode or mode == RoombaMode.PASSIVE:
      print("Roomba mode was not changed")
      return
    if mode == RoombaMode.OFF:
      self.connection.write(struct.pack('>B', 173))
      time.sleep(.02)
    elif mode == RoombaMode.SAFE:
      self.connection.write(struct.pack('>B', 131))
      time.sleep(.02)
      self.mode = RoombaMode.SAFE
    elif mode == RoombaMode.FULL:
      self.connection.write(struct.pack('>B', 132))
      time.sleep(.02)
      self.mode = RoombaMode.FULL
    print("Roomba mode changed")

  # drive the roomba using integrated velocity controllers
  # each wheel is controlled independently
  # velocity range is -500 to 500 mm/sec
  # integrated controller works in steps of 28.5 mm/sec
  def driveVel(self, right: int, left: int):
    if self.connection is None:
      print('connection to Roomba was not initialized')
      return
    if self.mode == RoombaMode.PASSIVE:
      print('instruction cannot be carried out because Roobma is in PASSIVE mode')
      return
    self.connection.write(struct.pack('>Bhh', 145, right, left))

  # drive the roomba using PWM
  # each wheel is controlled independently
  # PWM range is -255 to 255
  def drivePWM(self, right: int, left: int):
    if self.connection is None:
      print('connection to Roomba was not initialized')
      return
    if self.mode == RoombaMode.PASSIVE:
      print('instruction cannot be carried out because Roobma is in PASSIVE mode')
      return
    self.connection.write(struct.pack('>Bhh', 146, right, left))

  # set the LEDs on the roomba
  # power color ranges from 0 to 127, where 0 is green and 127 is red
  # power intensity ranges from 0 to 127, where 0 is off and 127 is max
  def setLEDs(self, check_led: bool, debris_led: bool, spot_led: bool, power_color: int, power_intensity: int):
    if self.connection is None:
      print('connection to Roomba was not initialized')
      return
    if self.mode == RoombaMode.PASSIVE:
      print('instruction cannot be carried out because Roobma is in PASSIVE mode')
      return
    self.connection.write(struct.pack(
        '>BBBB', 139, generateByte([check_led, 0, spot_led, debris_led]), power_color, power_intensity))

  # set the raw segments of the 7-segment display
  # digits on roomba are 3, 2, 1, 0 from left to right
  # see spec for segment labels because i dont feel like typing it all out here
  def setDigitsRaw(self, d3: int, d2: int, d1: int, d0: int):
    if self.connection is None:
      print('connection to Roomba was not initialized')
      return
    if self.mode == RoombaMode.PASSIVE:
      print('instruction cannot be carried out because Roobma is in PASSIVE mode')
      return
    self.connection.write(struct.pack('>BBBBB', 163, d3, d2, d1, d0))

  # set the segments of the 7-segment display to an ascii character
  # message must be exactly four characters
  # see spec for supported characters because i dont feel like typing it all out here
  def setDigitsASCII(self, msg: str):
    if self.connection is None:
      print('connection to Roomba was not initialized')
      return
    if self.mode == RoombaMode.PASSIVE:
      print('instruction cannot be carried out because Roobma is in PASSIVE mode')
      return
    if len(msg) != 4 or msg[0] not in cmd.ASCII_DIGITS.keys() or msg[1] not in cmd.ASCII_DIGITS.keys() or msg[2] not in cmd.ASCII_DIGITS.keys() or msg[3] not in cmd.ASCII_DIGITS.keys():
      print('one or more of your digits cannot be displayed')
      return
    self.connection.write(struct.pack(
        '>BBBBB', 164, cmd.ASCII_DIGITS[msg[0]], cmd.ASCII_DIGITS[msg[1]], cmd.ASCII_DIGITS[msg[2]], cmd.ASCII_DIGITS[msg[3]]))

  # begin sensor update loop in separate thread
  def beginUpdateLoop(self):
    self._updateThreadExit = False
    self._updateThread = threading.Thread(target=self.updateLoop)
    self.connection.write(struct.pack('>BBBBBB', 148, 4, 25, 26, 43, 44))
    self._updateThread.start()
    time.sleep(.015)

  # update sensors periodically and run user callbacks
  def updateLoop(self):
    update_data = False
    while (True):

        # wait for data to start
      if self._updateThreadExit or self.connection is None:
        break
      self.connection.read_until(struct.pack('>B', 19))

      # store time data
      update_time = time.time() / 1000
      time_diff = update_time - self.sensorData.update_time

      # get sensor data
      if self._updateThreadExit or self.connection is None:
        break
      raw_sensor_data = struct.unpack(
          '>BBhBhBhBhB', self.connection.read(14))

      # calculate new encoder positions
      diff_enc_left = raw_sensor_data[6] - self._prevEncLeft
      diff_enc_right = raw_sensor_data[8] - self._prevEncRight
      if diff_enc_left < -32768:
        diff_enc_left += 65536
      elif diff_enc_left > 32768:
        diff_enc_left -= 65536
      if diff_enc_right < -32768:
        diff_enc_right += 65536
      elif diff_enc_right > 32768:
        diff_enc_right -= 65536
      abs_enc_left = self.sensorData.enc_left + diff_enc_left
      abs_enc_right = self.sensorData.enc_right + diff_enc_right
      self._prevEncLeft = raw_sensor_data[6]
      self._prevEncRight = raw_sensor_data[8]

      # calculate velocities
      raw_vel_left = self.sensorData.vel_left
      raw_vel_right = self.sensorData.vel_right
      filtered_vel_left = raw_vel_left
      filtered_vel_right = raw_vel_right
      if time_diff != 0:
        raw_vel_left = diff_enc_left / time_diff / 1e3
        raw_vel_right = diff_enc_right / time_diff / 1e3

        filtered_vel_left = getMedian(
            raw_vel_left, self._prevVelLeft, self._prevPrevVelLeft)
        filtered_vel_right = getMedian(
            raw_vel_right, self._prevVelRight, self._prevPrevVelRight)

        filtered_vel_left = self.sensorData.vel_left * \
            self._vel_filter_str + filtered_vel_left * \
            (1 - self._vel_filter_str)
        filtered_vel_right = self.sensorData.vel_right * \
            self._vel_filter_str + filtered_vel_right * \
            (1 - self._vel_filter_str)

        self._prevPrevVelLeft = self._prevVelLeft
        self._prevVelLeft = raw_vel_left
        self._prevPrevVelRight = self._prevVelRight
        self._prevVelRight = raw_vel_right

      # update stored data
      if update_data and raw_sensor_data[4] != 0:
        self.sensorData.newData(
            update_time, raw_sensor_data[2] / raw_sensor_data[4], abs_enc_left, abs_enc_right, filtered_vel_left, filtered_vel_right)
      else:
        update_data = True

    print('Thread exited')


# generate a byte from a list of booleans
def generateByte(bits: List[bool], size: int = 8):
  p = bits[-size:]
  return sum(v << i for i, v in enumerate(p[::-1]))


def getMedian(a: int,  b: int,  c: int):
  x = a-b
  y = b-c
  z = a-c
  if x*y > 0:
    return b
  if x*z > 0:
    return c
  return a
