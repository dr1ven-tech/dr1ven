import numpy as np
import scipy
import time
import typing

from perception.tracking.constants import TRACKER_MISS_COUNT_MAX
from perception.tracking.entity import EntityTracker, EntityObservation

from utils.log import Log


class Tracker:
    """ Tracker maintains a list of tracked entities and lanes.
    """
    def __init__(
            self,
            initial_ego: EntityObservation,
            initial_now: float,
    ) -> None:
        self._ego_tracker = EntityTracker(
            initial_ego,
            initial_now,
        )

        self._trackers: typing.List[EntityTracker] = []

    def track(
            self,
            now: float,
            ego: EntityObservation,
            entities: typing.List[EntityObservation],
    ) -> None:
        self._ego_tracker.track(ego)

        start = time.time()

        cost = np.array((len(entities), len(self._trackers)))
        for i in range(len(entities)):
            for j in range(len(self._trackers)):
                cost[i][j] = self._trackers[j].mahalanobis(entities[i])

        row_ind, col_ind = scipy.optimize.linear_sum_assignment(cost)

        # Filter matches based on (im)possibility of the observation
        # transition.
        matches = np.zeros((len(entities), len(self._trackers)))
        matches_cost = 0.0
        for i in row_ind:
            for j in col_ind:
                if self._trackers[j].possible(entities[i]):
                    matches[i][j] = 1
                    matches_cost += cost[i][j]

        # Track or miss all existing trackers.
        for j in range(len(self._trackers)):
            if np.nonzero(matches[:, j])[0].shape[0] > 0:
                assert np.nonzero(matches[:, j])[0].shape[0] == 1
                i = np.nonzero(matches[:, j])[0][0]
                self._trackers[j].track(now, entities[i])
            else:
                self._trackers[j].track(now, None)

        # Create a tracker for all entities that were were not able to assign.
        new_count = 0
        for i in range(len(entities)):
            if np.nonzero(matches[i, :])[0].shape[0] == 0:
                new_count += 1
                self._trackers.append(EntityTracker(entities[i], now))

        # Remove tracker that have exceeded their miss count.
        removals_count = 0
        for i in reversed(range(len(self._trackers))):
            t = self._trackers[i]
            if t.miss_count() > TRACKER_MISS_COUNT_MAX:
                self._trackers.remove(t)

        Log.out(
            "Tracker assignement", {
                'trackers_count': len(self._trackers),
                'entities_count': len(entities),
                'matches_count': matches.sum(),
                'average_cost': matches_cost / matches.sum(),
                'new_count': new_count,
                'removals_count': removals_count,
                'processing_time': (time.time() - start),
            })

    def ego_tracker(
            self,
    ) -> EntityTracker:
        return self._ego_tracker

    def trackers(
            self,
    ) -> typing.List[EntityTracker]:
        return self._trackers
