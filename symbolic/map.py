import enum

import numpy as np

from symbolic.constants import HIGHWAY_LANES_COUNT
from symbolic.constants import HIGHWAY_DEPTH
from symbolic.constants import HIGHWAY_WIDTH
from symbolic.constants import HIGHWAY_HEIGHT

class RoadType(enum.Enum):
    INVALID = 0
    DRIVABLE = 1
    EMERGENCY = 2
    PARKING = 3

class LineType(enum.Enum):
    CONTINUOUS = 0
    DASHED = 1
    DENSE = 2

class Map:
    def __init__(
            self,
    ):
        self._component = np.zeros((
            HIGHWAY_LANES_COUNT,
            HIGHWAY_DEPTH, HIGHWAY_WIDTH,
            len(RoadType) + 2 * len(LineType),
        ))

