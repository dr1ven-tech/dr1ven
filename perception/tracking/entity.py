import numpy as np
import pykalman
import typing


class EntityObservation:
    """ EntityObservation repreents the tracked observations for an entity.

    The tracked observations are the position in continuous lane-centric
    coordinates (frontal and lateral) as well as the size (width and height) of
    the entity all expressed in meters (we want to apply the fitler before
    discretizing).
    """
    def __init__(
            self,
            position: typing.List[float],
            size: typing.List[float],
    ) -> None:
        assert len(position) == 2
        assert len(size) == 2

        self._position = position
        self._size = size

    def observation(
            self,
    ) -> np.ndarray:
        return np.array([
            self._position[0],
            self._position[1],
            self._size[0],
            self._size[1],
        ])


class EntityTracker:
    """ EntityTracker tracks an entity's position and size.

    See EntityObservation for information on the tracked dimensions.
    """
    def __init__(
            self,
            initial_observation: EntityObservation,
            initial_now: float,
    ) -> None:
        self._last_now = initial_now
        self._last_state_mean = np.array([
            initial_observation.observation()[0],
            initial_observation.observation()[1],
            0.0,
            0.0,
            initial_observation.observation()[2],
            initial_observation.observation()[3],
        ])
        self._last_state_covariance = np.zeros((6, 6))

        # Initialize a kallman filter by setting the observation matrix as well
        # as the initial state mean.
        self._kalman = pykalman.KalmanFilter(
            observation_matrices=np.array([
                [1, 0, 0, 0, 0, 0],
                [0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0],
                [0, 0, 0, 0, 0, 1],
            ]),
            initial_state_mean=self._last_state_mean,
            initial_state_covariance=self._last_state_covariance,
        )

        self._miss_count = 0

    def _update(
            self,
            now: float,
            observations: np.ndarray,
    ) -> None:
        dt = now - self._last_now
        assert dt > 0
        self._last_now = now

        self._last_state_mean, self._last_state_covariance = \
            self._kalman.filter_update(
                self._last_state_mean,
                self._last_state_covariance,
                observations,
                transition_matrix=np.array([
                    [1, 0, dt, 0, 0, 0],
                    [0, 1, 0, dt, 0, 0],
                    [0, 0, 1, 0, 0, 0],
                    [0, 0, 0, 1, 0, 0],
                    [0, 0, 0, 0, 1, 0],
                    [0, 0, 0, 0, 0, 1],
                ]),
            )

    def track(
            self,
            now: float,
            observation: typing.Optional[EntityObservation],
    ) -> None:
        if observation is None:
            self._miss_count += 1
            self._update(now, None)
        else:
            self._miss_count = 0
            self._update(now, observation.observation())

    def miss_count(
            self,
    ) -> int:
        return self._miss_count

    def position(
            self,
    ) -> typing.List[float]:
        return [
            self._last_state_mean[0],
            self._last_state_mean[1],
        ]

    def size(
            self,
    ) -> typing.List[float]:
        return [
            self._last_state_mean[4],
            self._last_state_mean[5],
        ]
