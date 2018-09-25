
from state.constants import HIGHWAY_LANE_DEPTH
from state.constants import HIGHWAY_LANE_WIDTH
from state.constants import HIGHWAY_LANE_HEIGHT

from state.lane import Lane, Section
from state.lane import RoadType

class Map:
    def __init__(
            self,
            lanes: typing.List[Lane] = [],
    ):
        self._lanes = lanes

    def __iter__(
            self,
    ):
        yield 'lanes', [dict(l) for l in self._lanes]

    @staticmethod
    def from_dict(
            spec,
    ) -> Map:
        return Map(
            [Lane.form_dict(l) for l in spec['lanes']],
        )
