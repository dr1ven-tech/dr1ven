import enum
import typing

from state.constants import HIGHWAY_LANE_DEPTH
from state.constants import HIGHWAY_LANE_WIDTH
from state.constants import HIGHWAY_LANE_HEIGHT

class EntityType(enum.Enum):
    NONE = 0
    EGO = 1
    UNKNOWN = 2
    CAR = 3
    TRUCK = 4
    MOTORBIKE = 5
    TRAFFIC_CONE = 6
    SAFETY_SIGN = 7
    HUMAN = 8
    ANIMAL = 9

class EntityOrientation(enum.Enum):
    FORWARD = 1
    LATERAL = 2

class EntityOccupation:
    def __init__(
            self,
            orientation: EntityOrientation,
            lane: int,
            position: typing.List[int],
            width: int,
            height: int,
    ):
        assert len(position) == 3
        assert position[0] >= 0 and position[0] < HIGHWAY_LANE_DEPTH
        assert position[1] >= 0 and position[1] < HIGHWAY_LANE_WIDTH
        assert position[2] >= 0 and position[2] < HIGHWAY_LANE_HEIGHT

        self._orientation = orientation
        self._lane = lane
        self._position = position
        self._width = width
        self._height = height

    def __iter__(
            self,
    ):
        yield 'orientation', self._orientation.value
        yield 'lane', self._lane
        yield 'position', self._position
        yield 'width', self._width
        yield 'height', self._height,

    def orientation(
            self,
    ) -> EntityOrientation:
        return self._orientation

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

class Entity:
    def __init__(
            self,
            type: EntityType,
            occupation: EntityOccupation,
            speed: typing.List[float],
    ):
        assert len(speed) == 3

        self._occupation = occupation
        self._type = type
        self._speed = speed

    def type(
            self,
    ) -> EntityType:
        return self._type

    def speed(
            self,
    ) -> typing.List[float]:
        return self._speed

    def occupation(
            self,
    ) -> EntityOccupation:
        return self._occupation

    def __iter__(
            self,
    ):
        yield 'type', self._type.value
        yield 'occupation', dict(self._occupation)
        yield 'speed', self._speed

