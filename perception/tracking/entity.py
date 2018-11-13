import numpy as np
import pykalman
import scipy
import typing

from perception.tracking.constants import \
    ENTITY_OBSERVATION_POSITION_TRANSITION_MAX


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

        self._array = np.array([
            self._position[0],
            self._position[1],
            self._size[0],
            self._size[1],
        ])

    def array(
            self,
    ) -> np.ndarray:
        return self._array


class EntityTracker:
    """ EntityTracker tracks an entity's position and size.

    See EntityObservation for information on the tracked dimensions.
    """
    def __init__(
            self,
            initial_observation: EntityObservation,
            initial_now: float,
    ) -> None:
        self._observation_matrices = np.array([
            [1, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 1],
        ])

        self._last_now = initial_now
        self._last_state_mean = np.array([
            initial_observation.array()[0],
            initial_observation.array()[1],
            0.0,
            0.0,
            initial_observation.array()[2],
            initial_observation.array()[3],
        ])
        # We initialize the coveriance matrix to the identify matrix which is a
        # sensible (and reversible) default.
        self._last_state_covariance = np.eye((6, 6))

        # Initialize a kallman filter by setting the observation matrix as well
        # as the initial state mean.
        self._kalman = pykalman.KalmanFilter(
            observation_matrices=self._observation_matrix,
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
            self._update(now, observation.array())

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

    def possible(
            self,
            observation: EntityObservation,
    ) -> bool:
        # TODO(stan): Iterate on definition of impossible observation
        # transitions.
        if abs(self._last_state_mean[0] - observation.array()[0]) > \
                ENTITY_OBSERVATION_POSITION_TRANSITION_MAX:
            return False
        if abs(self._last_state_mean[1] - observation.array()[1]) > \
                ENTITY_OBSERVATION_POSITION_TRANSITION_MAX:
            return False

    def mahalanobis(
            self,
            observation: EntityObservation,
    ) -> float:
        inv = np.linalg.inv(
            np.dot(
                np.dot(
                    self._observation_matrix,
                    self._last_state_covariance
                ),
                np.transpose(self._observation_matrix)
            )
        )

        obs = np.dot(
            self._observation_matrix,
            self._last_state_mean,
        )

        return scipy.spatial.distance.mahalanobis(
            observation.array(),
            obs,
            inv,
        )
