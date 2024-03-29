import enum
import typing

from state.constants import HIGHWAY_LANE_DEPTH
from state.constants import HIGHWAY_LANE_WIDTH
from state.constants import HIGHWAY_LANE_HEIGHT


class EntityType(enum.Enum):
    NONE = 0
    UNKNOWN = 1
    CAR = 2
    TRUCK = 3
    MOTORBIKE = 4
    BUS = 5
    TRAFFIC_CONE = 6
    SAFETY_SIGN = 7
    PERSON = 8
    ANIMAL = 9


class EntityOrientation(enum.Enum):
    FORWARD = 1
    LATERAL = 2


class EntityOccupation:
    def __init__(
            self,
            orientation: EntityOrientation,
            position: typing.List[int],
            width: int,
            height: int,
    ) -> None:
        assert len(position) == 3
        assert position[1] >= 0 and position[1] < HIGHWAY_LANE_DEPTH
        assert position[2] >= 0 and position[2] < HIGHWAY_LANE_HEIGHT

        self._orientation = orientation
        self._position = position
        self._width = width
        self._height = height

    def __iter__(
            self,
    ):
        yield 'orientation', self._orientation.value
        yield 'position', self._position
        yield 'width', self._width
        yield 'height', self._height,

    def orientation(
            self,
    ) -> EntityOrientation:
        return self._orientation

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

    def lane(
            self,
    ) -> int:
        return int(self._position[0] / HIGHWAY_LANE_WIDTH)


class Entity:
    def __init__(
            self,
            type: EntityType,
            id: str,
            occupation: EntityOccupation,
            velocity: typing.List[float],
    ) -> None:
        assert len(velocity) == 3

        self._id = id
        self._occupation = occupation
        self._type = type
        self._velocity = velocity

    def type(
            self,
    ) -> EntityType:
        return self._type

    def id(
            self,
    ) -> str:
        return self._id

    def velocity(
            self,
    ) -> typing.List[float]:
        return self._velocity

    def occupation(
            self,
    ) -> EntityOccupation:
        return self._occupation

    def __iter__(
            self,
    ):
        yield 'type', self._type.value
        yield 'occupation', dict(self._occupation)
        yield 'velocity', self._velocity
