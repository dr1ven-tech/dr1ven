import enum

import numpy as np

from symbolic.constants import HIGHWAY_LANE_COUNT
from symbolic.constants import HIGHWAY_LANE_DEPTH
from symbolic.constants import HIGHWAY_LANE_WIDTH
from symbolic.constants import HIGHWAY_LANE_HEIGHT

class RoadType(enum.Enum):
    INVALID = 0
    DRIVABLE = 1
    EMERGENCY = 2
    PARKING = 3

class Map:
    def __init__(
            self,
            specification,
    ):
        self._specification = specification
        self._component = np.zeros((
            HIGHWAY_LANE_COUNT,
            HIGHWAY_LANE_DEPTH, HIGHWAY_LANE_WIDTH,
            1,
        ), dtype=np.int8)

        for l in range(len(self._specification)):
            for section in self._specification[l]:
                start = section[0]
                end = section[1]
                types = section[2]
                for d in range(start, end):
                    for w in range(HIGHWAY_LANE_WIDTH):
                        self._component[l][d][w][0] = types[w].value

