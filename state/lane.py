import enum
import typing

import numpy as np

from state.constants import HIGHWAY_LANE_DEPTH
from state.constants import HIGHWAY_LANE_WIDTH
from state.constants import HIGHWAY_LANE_HEIGHT

class RoadType(enum.Enum):
    INVALID = 0
    DRIVABLE = 1
    EMERGENCY = 2
    PARKING = 3

class Section:
    def __init__(
            self,
            start: int = 0,
            end: int = HIGHWAY_LANE_DEPTH-1,
            slice: typing.List[RoadType] = (
                [RoadType.INVALID] * HIGHWAY_LANE_WIDTH
            ),
    ):
        assert len(slice) == HIGHWAY_LANE_WIDTH
        assert start >= 0
        assert end >= 0

        # We don't assert that end or start are smaller than HIGHWAY_LANE_DEPTH
        # as longer Lanes are relied upon by `motion.synthetic.Map`. Note that
        # this is checked when passed to a `state.Highway` constructor.

        self._start = start
        self._end = end
        self._slice = slice

    def start(
            self,
    ) -> int:
        return self._start

    def end(
            self,
    ) -> int:
        return self._end

    def slice(
            self,
    ) -> typing.List[RoadType]:
        return self._slice

    def __iter__(
            self,
    ):
        yield 'start', self._start
        yield 'end', self._end
        yield 'slice', [t.value for t in self._slice]

    @staticmethod
    def from_dict(
            spec,
    ):
        return Section(
            spec['start'],
            spec['end'],
            [RoadType(t) for t in spec['slice']],
        )


class Lane:
    def __init__(
            self,
            sections: typing.List[Section] = [
                Section(),
            ],
    ):
        self._sections = sections

    def sections(
            self,
    ) -> typing.List[Section]:
        return self._sections

    def __iter__(
            self,
    ):
        yield 'sections', [dict(s) for s in self._sections]

    @staticmethod
    def from_dict(
            spec,
    ):
        return Lane(
            [Section.from_dict(s) for s in spec['sections']],
        )
