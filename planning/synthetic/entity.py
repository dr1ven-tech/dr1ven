import typing

from state.constants import HIGHWAY_LANE_WIDTH
from state.constants import HIGHWAY_LANE_HEIGHT
from state.highway import Highway
from state.entity import EntityType


class SyntheticEntity:
    """ `SyntheticEntity` represents a simulated entity.

    While `state.Entity` does not have any depth, `SyntheticEntity` keeps track
    of the depth of the object. The position of the entity is equivalent to the
    position of the `state.Entity` (front-left corner).
    """
    def __init__(
            self,
            id: str,
            position: typing.List[int],
            shape: typing.List[int],
            velocity: typing.List[float],
    ) -> None:
        assert len(position) == 3
        assert len(shape) == 3
        assert len(velocity) == 3

        assert position[1] >= 0
        assert position[2] >= 0 and position[2] < HIGHWAY_LANE_HEIGHT

        self._position = position
        self._shape = shape
        self._velocity = velocity
        self._id = id

    def type(
            self,
    ) -> EntityType:
        raise Exception("Not implemented")

    def id(
            self,
    ) -> str:
        return self._id

    def step(
            self,
            step: int,
            delta: float,
            state: Highway,
    ) -> None:
        raise Exception("Not implemented")

    def position(
            self,
    ) -> typing.List[int]:
        return self._position

    def shape(
            self,
    ) -> typing.List[int]:
        return self._shape

    def velocity(
            self,
    ) -> typing.List[float]:
        return self._velocity

    def lane(
            self,
    ) -> int:
        return int(self._position[0] / HIGHWAY_LANE_WIDTH)

    def collide(
            self,
            other,
    ) -> bool:
        collide = True
        for i in range(3):
            collide = collide and (
                self.position()[i] < other.position()[i] + other.shape()[i] and
                self.position()[i] + self.shape()[i] > other.position()[i]
            )
        return collide
