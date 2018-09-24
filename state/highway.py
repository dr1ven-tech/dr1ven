import numpy as np

from state.constants import HIGHWAY_LANE_COUNT
from state.constants import HIGHWAY_LANE_DEPTH
from state.constants import HIGHWAY_LANE_WIDTH
from state.constants import HIGHWAY_LANE_HEIGHT

from state.entity import EntityType
from state.entity import Entity

from state.lane import Lane

class Highway:
    def __init__(
            self,
    ):
        self._lanes = [Lane()] * HIGHWAY_LANE_COUNT
        self._entities = []
        self._ego = None

    def add_entity(
            self,
            entity: Entity,
    ) -> None:
        self._entities.append(entity)

        if entity.type() == EntityType.EGO:
            assert self.ego is None
            self._ego = entity

    def set_lanes(
            self,
            position: int,
            lane: Lane,
    ) -> None:
        self._map = m

