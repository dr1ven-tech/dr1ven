import typing

from state.constants import HIGHWAY_LANE_DEPTH
from state.constants import EGO_POSITION_DEPTH

from state.entity import Entity

from state.lane import Lane


class Highway:
    """ `Highway` encodes a symbolic representation of an highway region.

    It represents the state of an highway in the vicinity (depth
    `HIGHWAY_LANE_DEPTH`) of an ego entity.

    By convention the ego entity must be positioned (depth) at
    `EGO_POSITION_DEPTH`.
    """
    def __init__(
            self,
            lanes: typing.List[Lane],
            ego: Entity,
            entities: typing.List[Entity],
    ) -> None:
        self._lanes = lanes
        self._entities = entities
        self._ego = ego

        for l in lanes:
            for s in l.sections():
                assert s.start() >= 0
                assert s.end() < HIGHWAY_LANE_DEPTH

        assert ego.occupation().position()[1] == EGO_POSITION_DEPTH

        for e in entities:
            assert ego.id() != e.id()
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
    ) -> typing.Optional[Entity]:
        return self._ego

    def __iter__(
            self,
    ):
        yield 'lanes', [dict(l) for l in self._lanes]
        yield 'ego', dict(self._ego)
        yield 'entities', [dict(e) for e in self._entities]
