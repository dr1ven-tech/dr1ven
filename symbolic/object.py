import enum

import numpy as np

from constants import HIGHWAY_LANES_COUNT
from constants import HIGHWAY_DEPTH
from constants import HIGHWAY_WIDTH
from constants import HIGHWAY_HEIGHT

class ObjectType(enum.Enum):
    NONE = 0
    EGO = 1
    UNKNOWN = 2
    CAR = 3
    TRUCK = 4
    MOTORBIKE = 5
    TRAFFIC_CONE = 6
    SAFETY_SIGN = 7
    HUMAN = 8
    ANIMAL = 9

class Object:
    def __init__(
            self,
            type,
            occupation,
            speed,
    ):
        self._occupation = occupation
        self._type = type
        self._speed = speed
