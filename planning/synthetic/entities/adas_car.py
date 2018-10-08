import typing

from state.constants import EGO_POSITION_DEPTH
from state.highway import Highway
from state.entity import EntityType
from planning.synthetic.entity import SyntheticEntity

ADAS_SECURITY_DISTANCE = 100
ADAS_SPEED_TRACKING_FACTOR = 3


class ADASCar(SyntheticEntity):
    def __init__(
            self,
            id: str,
            position: typing.List[float],
            shape: typing.List[float],
            desired_speed: float,
    ) -> None:
        super(ADASCar, self).__init__(
            id,
            position,
            shape,
            [0.0, desired_speed, 0.0],
        )

        # _float_position is the float position of the car in voxel width. The
        # speed is also expressed in voxels per seconds.
        self._float_position = float(self._position[1])
        self._desired_speed = desired_speed

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
        target_speed = self._desired_speed

        # Detect any vehicule within safety distance (50m)
        for e in state.entities():
            if e.occupation().lane() == self.lane() and (
                    e.occupation().position()[1] > EGO_POSITION_DEPTH and
                    e.occupation().position()[1] <= (
                        EGO_POSITION_DEPTH + ADAS_SECURITY_DISTANCE
                    )
            ):
                target_speed = min(target_speed, e.velocity()[1])

        # Update current velocity with the newly calculated target_speed.
        self._velocity[1] -= (self._velocity[1] - target_speed) / 3

        # Integrate position.
        self._float_position = self._float_position + delta * self._velocity[1]
        self._position[1] = int(self._float_position)

    @staticmethod
    def from_dict(
            spec,
    ):
        return ADASCar(
            spec['id'],
            spec['position'],
            spec['shape'],
            spec['desired_speed'],
        )
