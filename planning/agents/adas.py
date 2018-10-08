from state.constants import EGO_POSITION_DEPTH
from state.constants import HIGHWAY_LANE_DEPTH
from state.constants import HIGHWAY_LANE_WIDTH
from state.highway import Highway
from planning.agent import Agent, Action, Command

ADAS_SAFETY_DISTANCE = 150
ADAS_COMMAND_DELTA = 1


class ADAS(Agent):
    def __init__(
            self,
            desired_speed: float,
    ) -> None:
        super(ADAS, self).__init__()

        self._desired_speed = desired_speed
        self._lane = None

    def type(
            self,
    ) -> str:
        return 'adas'

    def action(
            self,
            time: float,
            state: Highway,
    ) -> Action:
        if self._lane is None:
            self._lane = state.ego().occupation().lane()

        # Detect any vehicule within safety distance.
        front = None
        distance = HIGHWAY_LANE_DEPTH
        for e in state.entities():
            if e.occupation().lane() == self.lane() and (
                    e.occupation().position()[1] > EGO_POSITION_DEPTH and
                    e.occupation().position()[1] <= (
                        EGO_POSITION_DEPTH + ADAS_SAFETY_DISTANCE
                    )
            ):
                d = e.occupation().position()[1] - EGO_POSITION_DEPTH
                if d <= distance:
                    d = distance
                    front = e

        forward = Command(
            int(EGO_POSITION_DEPTH +
                self._desired_speed * ADAS_COMMAND_DELTA),
            ADAS_COMMAND_DELTA,
        )

        if front is not None:
            target = int(front.position()[1] +
                         front.velocity()[1] * ADAS_COMMAND_DELTA)
            if target < forward.position:
                forward = Command(target, ADAS_COMMAND_DELTA)

        lateral = Command(
            self._lane * HIGHWAY_LANE_WIDTH + 1,
            ADAS_COMMAND_DELTA,
        )

        return Action(
            forward,
            lateral,
        )

    @staticmethod
    def from_dict(
            spec,
    ):
        return ADAS(
            spec['desired_speed'],
        )
