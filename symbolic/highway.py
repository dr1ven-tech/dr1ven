import numpy as np

from symbolic.constants import HIGHWAY_LANES_COUNT
from symbolic.constants import HIGHWAY_DEPTH
from symbolic.constants import HIGHWAY_WIDTH
from symbolic.constants import HIGHWAY_HEIGHT

from symbolic.object import ObjectType
from symbolic.object import Object

from symbolic.map import RoadType
from symbolic.map import LineType
from symbolic.map import Map

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
        self.ego = None

    def add_object(
            self,
            object,
    ):
        for o in object._occupation:
            occ = self._objects_component[tuple(o)]

            for t in ObjectType:
                occ[t.value] = 0.0
            occ[object.type().value] = 1.0

            occ[len(ObjectType) + 0] = object.speed()[0]
            occ[len(ObjectType) + 1] = object.speed()[1]
            occ[len(ObjectType) + 2] = object.speed()[2]

        self._objects.append(object)

        if object.type() == ObjectType.EGO:
            assert self.ego is None
            self.ego = object

    def set_map(
            self,
            map,
    ):
        self._map_component = map._component

