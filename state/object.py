import numpy as np

from state.constants import HIGHWAY_LANES_COUNT
from state.constants import HIGHWAY_DEPTH
from state.constants import HIGHWAY_WIDTH
from state.constants import HIGHWAY_HEIGHT
from state.constatns import NONE_TYPE

OBJECT_TYPES = [
    'ego',
    'unknown',
    'car',
    'truck',
    'motorbike',
    'traffic_cone',
    'safety_sign',
    'human',
    'animal',
]

class Object:
    def __init__(
            self,
            object_type,
            speed,
    ):
        self._compoment = np.zeros((
            HIGHWAY_LANE_COUNT,
            HIGHWAY_DEPTH, HIGHWAY_WIDTH, HIGHWAY_HEIGHT,
            len(OBJECT_TYPES) + 3
        ))

        self._type = object_type
        self._speed = speed
