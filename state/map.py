import enum

import numpy as np

from constants import HIGHWAY_LANES_COUNT
from constants import HIGHWAY_DEPTH
from constants import HIGHWAY_WIDTH
from constants import HIGHWAY_HEIGHT

class RoadType(enum.Enum):
    NONE = 0
    DRIVABLE = 1
    EMERGENCY = 2
    PARKING = 3

class LineType(enum.Enum):
    NONE = 0
    CONTINUOUS = 1
    DASHED = 2
    DENSE = 3

class Map:
    def __init__(
            self,
    ):
        self._component = np.zeros((
            HIGHWAY_LANES_COUNT,
            HIGHWAY_DEPTH, HIGHWAY_WIDTH,
            len(RoadType) + 2 * len(LineType),
        ))

