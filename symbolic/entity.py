import enum

import numpy as np

from symbolic.constants import HIGHWAY_LANE_COUNT
from symbolic.constants import HIGHWAY_LANE_DEPTH
from symbolic.constants import HIGHWAY_LANE_WIDTH
from symbolic.constants import HIGHWAY_LANE_HEIGHT

class EntityType(enum.Enum):
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

class EntityOrientation(enum.Enum):
    FORWARD = 1
    LATERAL = 2


class EntityOccupation:
    def __init__(
            self,
            orientation,
            lane,
            position,
            width,
            height,
    ):
        assert lane < HIGHWAY_LANE_COUNT

        assert position[0] < HIGHWAY_LANE_DEPTH
        assert position[1] < HIGHWAY_LANE_WIDTH
        assert position[2] < HIGHWAY_LANE_HEIGHT

        self._orientation = orientation
        self._lane = lane
        self._position = position
        self._width = width
        self._height = height

class Entity:
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

    def occupation(
            self,
    ):
        return self._occupation
