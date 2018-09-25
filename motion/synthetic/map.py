import json
import os
import typing

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
    ):
        return Map(
            [Lane.from_dict(l) for l in spec['lanes']],
        )

    @staticmethod
    def from_file(
            path: str,
    ):
        with open(path) as f:
            return Map.from_dict(json.load(f))



def test():
    m = Map.from_file(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            './maps/highway_3lanes_10k.json',
        )
    )

    print("{}".format(dict(m)))
