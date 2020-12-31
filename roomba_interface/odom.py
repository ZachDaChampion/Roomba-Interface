import math
from enum import Enum


class LengthUnits(Enum):
  MM = .001
  CM = .01
  METER = 1
  INCH = 39.3701
  FOOT = 3.28084
  YARD = 1.09361


class AngleUnits(Enum):
  RADIAN = 1
  DEGREE = 180 / math.pi


class Pose:
  _x = 0  # meters
  _y = 0  # meters
  _angle = 0  # radians

  def __init__(self, x, y, angle):
    self._x = x
    self._y = y
    self._angle = angle

  def x(self, unit: LengthUnits = LengthUnits.INCH):
    return self._x * unit.value

  def y(self, unit: LengthUnits = LengthUnits.INCH):
    return self._y * unit.value

  def angle(self, unit: AngleUnits = AngleUnits.RADIAN):
    return self._angle * unit.value


class Odom:
  pose: Pose = Pose(0, 0, 0)
  encoder_conversion = math.pi * 3 / 21200  # ticks to meter
  wheelbase_width = .235  # width of wheelbase

  def __init__(self):
    pass

  # update odom calculation
  def update(self, change_enc_left, change_enc_right, abs_enc_left, abs_enc_right):

    # calculate distances (meters)
    d = (change_enc_left * self.encoder_conversion +
         change_enc_right * self.encoder_conversion) / 2

    # calculate new angle (radians)
    angle_new = (abs_enc_right - abs_enc_left) * \
        self.encoder_conversion / self.wheelbase_width
    a = angle_new - self.pose._angle

    # integrate normally if motion is purely linear
    if (a == 0):
      self.pose = Pose(self.pose._x + d * math.cos(angle_new),
                       self.pose._y + d * math.sin(angle_new), angle_new)

    # integrate along an arc
    else:

      # calculate radius of arc
      radius = d / a

      # for *efficiency*
      cos_a = math.cos(a)
      sin_a = math.sin(a)

      # calculate new coords relative to roomba
      rel_x = radius * sin_a  # cos(x - 90 deg) = sin(x)
      rel_y = radius * (1 - cos_a)  # sin(x - 90 deg) = -cos(x)

      # rotate to be world-centric
      cos_a = math.cos(self.pose._angle)
      sin_a = math.sin(self.pose._angle)
      change_x = rel_x * cos_a - rel_y * sin_a
      change_y = rel_y * cos_a + rel_x * sin_a

      # add to current pose
      self.pose = Pose(self.pose._x + change_x,
                       self.pose._y + change_y, angle_new)
    return self.pose
