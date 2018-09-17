import numpy as np

from state.constants import HIGHWAY_LANES_COUNT
from state.constants import HIGHWAY_DEPTH
from state.constants import HIGHWAY_WIDTH
from state.constants import HIGHWAY_HEIGHT
from state.constatns import NONE_TYPE

from state.object import OBJECT_TYPES
from state.object import Object

from state.map import ROAD_TYPES
from state.map import LINE_TYPES
from state.map import Map

class Highway:
    def __init__(
            self,
    ):
        self._map_component = np.zeros((
            HIGHWAY_LANE_COUNT,
            HIGHWAY_DEPTH, HIGHWAY_WIDTH,
            len(ROAD_TYPES) + 2 * len(LINE_TYPES),
        ))
        self._objects_compoment = np.zeros((
            HIGHWAY_LANE_COUNT,
            HIGHWAY_DEPTH, HIGHWAY_WIDTH, HIGHWAY_HEIGHT,
            len(OBJECT_TYPES) + 3
        ))
        self._objects = []

    def add_object(
            o:Object,
    ):
        self._object_component += o._component
        self._objects.append(o)

    def set_map(
            m:Map,
    ):
        self._map_component = m._component

if __name__ == "__main__":
    r = Highway()
    v = r.voxel(0, 0, 0, 0)

