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
            lane: int,
            position: typing.List[int],
            shape: typing.List[int],
            velocity: typing.List[float],
    ) -> None:
        assert len(position) == 3
        assert len(shape) == 3
        assert len(velocity) == 3

        assert position[0] >= 0 and position[0] < HIGHWAY_LANE_WIDTH
        assert position[1] >= 0
        assert position[2] >= 0 and position[2] < HIGHWAY_LANE_HEIGHT

        self._lane = lane
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

    def velocity(
            self,
    ) -> typing.List[float]:
        return self._velocity


class ADASCar(SyntheticEntity):
    def __init__(
            self,
            id: str,
            lane: int,
            position: typing.List[int],
            shape: typing.List[int],
            speed: float,
    ) -> None:
        super(ADASCar, self).__init__(
            id,
            lane,
            position,
            shape,
            [0.0, speed, 0.0],
        )

        # _float_position is the float position of the car in voxel width. The
        # speed is also expressed in voxels per seconds.
        self._float_position = float(self._position[1])

    def type(
            self,
    ) -> EntityType:
        return EntityType.CAR

    def step(
            self,
            step: int,
            delta: float,
            state: Highway,
    ):
        # Maintain current speed and lateral position.
        self._float_position = self._float_position + delta * self._velocity[1]
        self._position[1] = int(self._float_position)

    @staticmethod
    def from_dict(
            spec,
    ):
        return ADASCar(
            spec['id'],
            spec['lane'],
            spec['position'],
            spec['shape'],
            spec['speed'],
        )
