import numpy as np
import typing

from perception.tracking.entity import EntityTracker, EntityObservation


class Tracker:
    """ Tracker maintains a list of tracked entities and lanes.
    """
    def __init__(
            self,
            initial_ego: EntityObservation,
            initial_now: float,
    ) -> None:
        self.ego_tracker = EntityTracker(
            initial_ego,
            initial_now,
        )

        self._entitiy_trackers = []

    def track(
            self,
            now: float,
            ego: EntityObservation,
            entities: typing.List[EntityObservation],
    ) -> None:
        self.ego_tracker.track(ego)

        # TODO(stan): algorithm to match observations to existing trackers.

    def ego_tracker(
            self,
    ) -> EntityTracker:
        return self._ego_tracker

    def trackers(
            self,
    ) -> typing.List[EntityTracker]:
        return self._entity_trackers
