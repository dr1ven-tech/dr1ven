import copy
import enum
import typing

from state.constants import HIGHWAY_LANE_DEPTH
from state.constants import HIGHWAY_LANE_WIDTH


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
                [RoadType.INVALID] * HIGHWAY_LANE_WIDTH * 5
            ),
    ) -> None:
        assert len(slice) >= HIGHWAY_LANE_WIDTH
        assert start >= 0
        assert end >= 0
        assert start < end

        # We don't assert that end or start are smaller than HIGHWAY_LANE_DEPTH
        # as longer Lanes are relied upon by `planning.synthetic.Map`. Note that
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

    def truncate(
            self,
            start: int,
            end: int,
    ):
        assert start >= 0
        assert end >= 0
        assert start < end

        if start >= self._end or end <= self._start:
            return None

        return Section(
            max(start, self._start)-start,
            min(end, self._end)-start,
            copy.copy(self._slice),
        )

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
