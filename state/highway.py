import typing

from state.constants import HIGHWAY_LANE_DEPTH
from state.constants import HIGHWAY_LANE_WIDTH
from state.constants import HIGHWAY_LANE_HEIGHT

from state.entity import EntityType
from state.entity import Entity

from state.lane import Lane

class Highway:
    def __init__(
            self,
            lanes: typing.List[Lane] = [],
            entities: typing.List[Entity] = [],
    ):
        self._lanes = lanes
        self._entities = entities
        self._ego = None

        for l in lanes:
            for s in l.sections():
                assert s.start() >= 0
                assert s.end() < HIGHWAY_LANE_DEPTH
        for e in entities:
            if e.type() == EntityType.EGO:
                assert self._ego is None
                self._ego = e
            assert e.occupation().lane() < len(self._lanes)

    def lanes(
            self,
    ) -> typing.List[Lane]:
        return self._lanes

    def entities(
            self,
    ) -> typing.List[Entity]:
        return self._entities

    def ego(
            self,
    ) -> Entity:
        return self._ego

    def __iter__(
            self,
    ):
        yield 'lanes', [dict(l) for l in self._lanes]
        yield 'entities', [dict(e) for e in self._entities]

