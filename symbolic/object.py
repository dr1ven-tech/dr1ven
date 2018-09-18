import enum

import numpy as np

from symbolic.constants import HIGHWAY_LANES_COUNT
from symbolic.constants import HIGHWAY_DEPTH
from symbolic.constants import HIGHWAY_WIDTH
from symbolic.constants import HIGHWAY_HEIGHT

class ObjectType(enum.Enum):
    EGO = 0
    UNKNOWN = 1
    CAR = 2
    TRUCK = 3
    MOTORBIKE = 4
    TRAFFIC_CONE = 5
    SAFETY_SIGN = 6
    HUMAN = 7
    ANIMAL = 8

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

    def type(
            self,
    ):
        return self._type

    def speed(
            self,
    ):
        return self._speed
