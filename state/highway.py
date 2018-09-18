import numpy as np

from constants import HIGHWAY_LANES_COUNT
from constants import HIGHWAY_DEPTH
from constants import HIGHWAY_WIDTH
from constants import HIGHWAY_HEIGHT

from object import ObjectType
from object import Object

from map import RoadType
from map import LineType
from map import Map

class Highway:
    def __init__(
            self,
    ):
        self._map_component = np.zeros((
            HIGHWAY_LANES_COUNT,
            HIGHWAY_DEPTH, HIGHWAY_WIDTH,
            len(RoadType) + 2 * len(LineType),
        ))
        self._objects_component = np.zeros((
            HIGHWAY_LANES_COUNT,
            HIGHWAY_DEPTH, HIGHWAY_WIDTH, HIGHWAY_HEIGHT,
            len(ObjectType) + 3
        ))
        self._objects = []

    def add_object(
            self,
            object,
    ):
        for o in object._occupation:
            occ = self._objects_component[tuple(o)]
            occ[object._type.value] = 1.0
            occ[len(ObjectType) + 0] = object._speed[0]
            occ[len(ObjectType) + 1] = object._speed[1]
            occ[len(ObjectType) + 2] = object._speed[2]

        self._objects.append(object)

    def set_map(
            self,
            map,
    ):
        self._map_component = map._component

