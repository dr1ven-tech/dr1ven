import numpy as np

from symbolic.constants import HIGHWAY_LANE_COUNT
from symbolic.constants import HIGHWAY_LANE_DEPTH
from symbolic.constants import HIGHWAY_LANE_WIDTH
from symbolic.constants import HIGHWAY_LANE_HEIGHT

from symbolic.entity import EntityType
from symbolic.entity import Entity

from symbolic.map import RoadType
from symbolic.map import Map

class Highway:
    def __init__(
            self,
    ):
        self._map = None
        self._entities = []
        self.ego = None

    def add_entity(
            self,
            entity,
    ):
        self._entities.append(entity)

        if entity.type() == EntityType.EGO:
            assert self.ego is None
            self.ego = entity

    def set_map(
            self,
            m,
    ):
        self._map = m

