import typing

from state.constants import HIGHWAY_LANE_DEPTH
from state.constants import EGO_POSITION_DEPTH

from state.entity import Entity
from state.section import Section


class Highway:
    """ `Highway` encodes a symbolic representation of an highway region.

    It represents the state of an highway in the vicinity (depth
    `HIGHWAY_LANE_DEPTH`) of an ego entity and consists in:

    - `sections`: a list of sections that encode the state of the road in a
      region going from `0` to `HIGHWAY_LANE_DEPTH`.
    - `ego`: an ego entity positioned by convention at `EGO_POSITION_DEPTH`
      (depth).
    - `entities`: a list of entities present in the region.
    """
    def __init__(
            self,
            sections: typing.List[Section],
            ego: Entity,
            entities: typing.List[Entity],
    ) -> None:
        self._sections = sections
        self._entities = entities
        self._ego = ego

        assert len(sections) > 0
        slice_width = len(sections[0].slice())

        for s in sections:
            assert s.start() >= 0
            assert s.end() < HIGHWAY_LANE_DEPTH
            assert len(s.slice()) == slice_width

        assert ego.occupation().position()[0] < slice_width
        assert ego.occupation().position()[1] == EGO_POSITION_DEPTH

        for e in entities:
            assert ego.id() != e.id()
            assert e.occupation().position()[0] < slice_width

    def sections(
            self,
    ) -> typing.List[Section]:
        return self._sections

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
        yield 'sections', [dict(s) for s in self._sections]
        yield 'ego', dict(self._ego)
        yield 'entities', [dict(e) for e in self._entities]
