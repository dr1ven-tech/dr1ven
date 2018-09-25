import typing

from state.constants import HIGHWAY_LANE_WIDTH
from state.constants import HIGHWAY_LANE_HEIGHT
from state.entity import EntityType

class Entity:
    def __init__(
            self,
            lane: int,
            position: typing.List[int],
            shape: typing.List[int],
    ) -> None:
        assert len(position) == 3
        assert position[0] >= 0 and position[0] < HIGHWAY_LANE_WIDTH
        assert position[1] >= 0
        assert position[2] >= 0 and position[2] < HIGHWAY_LANE_HEIGHT

        assert len(shape) == 3

        self._lane = 0
        self._position = position
        self._shape = shape

    def step(
            self,
            delta: float,
    ):
        raise Exception("Not implemented")

    def type(
            self,
    ) -> EntityType:
        raise Exception("Not implemented")

    def lane(
            self,
    ) -> int:
        return self._lane

    def position(
            self,
    ) -> typing.List[int]:
        return self._position

    def shape(
            self,
    ) -> typing.List[int]:
        return self._shape
