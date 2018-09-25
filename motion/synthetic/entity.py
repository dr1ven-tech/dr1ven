import typing

from state.constants import HIGHWAY_LANE_WIDTH
from state.constants import HIGHWAY_LANE_HEIGHT
from state.entity import EntityType

class Entity:
    def __init__(
            self,
            lane: int,
            position: typing.List[int],
            width: int,
            height: int,
            depth: int,
    ) -> None:
        assert len(position) == 3
        assert position[0] >= 0
        assert position[1] >= 0 and position[1] < HIGHWAY_LANE_WIDTH
        assert position[2] >= 0 and position[2] < HIGHWAY_LANE_HEIGHT

        self._lane = 0
        self._position = position
        self._width = width
        self._height = height
        self._depth = depth

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

    def width(
            self,
    ) -> int:
        return self._width

    def height(
            self,
    ) -> int:
        return self._height

    def depth(
            self,
    ) -> int:
        return self._depth
