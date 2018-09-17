import numpy as np

from state.constants import HIGHWAY_LANES_COUNT
from state.constants import HIGHWAY_DEPTH
from state.constants import HIGHWAY_WIDTH
from state.constants import HIGHWAY_HEIGHT
from state.constatns import NONE_TYPE

ROAD_TYPES = [
    'drivable',
    'emergency',
    'parking',
]

LINE_TYPES = [
    'continuous',
    'dashed',
    'dense_dashed',
]

class Map:
    def __init__(
            self,
    ):
        self._compoment = np.zeros((
            HIGHWAY_LANE_COUNT,
            HIGHWAY_DEPTH, HIGHWAY_WIDTH,
            len(ROAD_TYPES) + 2 * len(LINE_TYPES),
        ))

