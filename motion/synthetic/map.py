import json
import os
import typing

from utils.log import Log

from state.constants import HIGHWAY_LANE_DEPTH
from state.constants import HIGHWAY_LANE_WIDTH
from state.constants import HIGHWAY_LANE_HEIGHT

from state.lane import Lane, Section
from state.lane import RoadType

class Map:
    def __init__(
            self,
            lanes: typing.List[Lane] = [],
    ) -> None:
        self._lanes = lanes

    def truncate(
            self,
            start: int,
            end: int,
    ) -> typing.List[Lane]:
        return [l.truncate(start, end) for l in self._lanes]

    def __iter__(
            self,
    ):
        yield 'lanes', [dict(l) for l in self._lanes]

    @staticmethod
    def from_dict(
            spec,
    ):
        return Map(
            [Lane.from_dict(l) for l in spec['lanes']],
        )

    @staticmethod
    def from_file(
            path: str,
    ):
        Log.out("Loading map", {
            'path': path,
        })
        with open(path) as f:
            return Map.from_dict(json.load(f))
