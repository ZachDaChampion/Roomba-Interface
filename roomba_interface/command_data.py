from enum import Enum


class _MtrCmdMode(Enum):
  OFF = 0
  VELRAD = 1
  VEL = 2
  PWM = 3


class _DigitsCmdMode(Enum):
  OFF = 0
  RAW = 1
  ASCII = 2


# control
START = 128
RESET = 7
STOP = 173
BAUD = 129
SAFE = 131
FULL = 132
DOCK = 143
POWER = 133

# motors
DRIVE = 137
DRIVE_DIRECT = 145
DRIVE_PWM = 146
MOTORS = 138
MOTORS_PWM = 144

# lights
LEDS = 139
DIGITS_RAW = 163
DIGITS_ASCII = 164

# sensors
SENSORS = 142
SENSOR_QUERY_LIST = 149
SENSOR_STREAM = 148
SENSOR_STREAM_PAUSE_RESUME = 150
BUMPS_WHEELDROPS = 7
WALL = 8
CLIFF_LEFT = 9
CLIFF_FRONT_LEFT = 10
CLIFF_FRONT_RIGHT = 11
CLIFF_RIGHT = 12
VIRTUAL_WALL = 13
WHEEL_OVERCURRENTS = 14
DIRT_DETECT = 15
BUTTONS = 18
DISTANCE = 19
ANGLE = 20
CHARGE_STATE = 21
VOLTAGE = 22
CURRENT = 23
BATTERY_TEMP = 24
BATTERY_CHARGE = 25
BATTERY_CAPACITY = 26
WALL_SIGNAL = 27
CLIFF_LEFT_SIGNAL = 28
CLIFF_FRONT_LEFT_SIGNAL = 29
CLIFF_FRONT_RIGHT_SIGNAL = 30
CLIFF_RIGHT_SIGNAL = 31
OI_MODE = 35
REQ_VEL = 39
REQ_RADIUS = 40
REQ_VEL_RIGHT = 41
REQ_VEL_LEFT = 42
ENC_LEFT = 43
ENC_RIGHT = 44
LIGHT_BUMPER = 45
MOTOR_CURRENT_LEFT = 54
MOTOR_CURRENT_RIGHT = 55
STASIS = 58


ASCII_DIGITS = {
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
