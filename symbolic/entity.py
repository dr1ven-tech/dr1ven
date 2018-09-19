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

    @staticmethod
    def forward_occupation(
            lane,
            forward_position,
            width,
            height,
            lane_offset,
    ):
        assert lane_offset < HIGHWAY_LANE_WIDTH

        occupation = []
        for w in range(width):
            for h in range(height):
                wp = w + lane_offset
                if wp < HIGHWAY_LANE_WIDTH:
                    occupation.append(
                        (lane, forward_position, wp, h),
                    )
                elif lane > 0:
                    occupation.append(
                        (lane-1, forward_position, HIGHWAY_LANE_WIDTH - wp, h),
                    )

        return occupation

    @staticmethod
    def lateral_occupation(
            lane,
            forward_position,
            width,
            height,
            lane_offset,
    ):
        assert offset < HIGHWAY_LANE_WIDTH

        occupation = []
        for w in range(width):
            for h in range(height):
                occupation.append(
                    (lane, forward_position + depth, lane_offset, h),
                )

        return occupation
