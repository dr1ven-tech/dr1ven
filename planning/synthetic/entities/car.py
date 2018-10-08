import typing

from state.constants import EGO_POSITION_DEPTH
from state.entity import EntityType
from state.highway import Highway

from planning.agent import Agent
from planning.agents.adas import ADAS
from planning.synthetic.entity import SyntheticEntity

CAR_EXECUTION_DAMPING = 3


class Car(SyntheticEntity):
    def __init__(
            self,
            id: str,
            position: typing.List[float],
            shape: typing.List[float],
            velocity: typing.List[float],
            agent: Agent,
    ) -> None:
        super(Car, self).__init__(
            id,
            position,
            shape,
            velocity,
        )

        assert agent is not None

        self._agent = agent

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
        # Receive action from planning agent.
        action = self._agent.action(step * delta, state)

        # Execute motion in simulated space based on received action.
        forward_speed = \
            float(action.forward().position() - EGO_POSITION_DEPTH) / \
            action.forward().delta()
        self._velocity[1] -= \
            (self._velocity[1] - forward_speed) / CAR_EXECUTION_DAMPING
        self._position[1] = self._position[1] + delta * self._velocity[1]

        lateral_speed = \
            (float(action.lateral().position()) - self.position()[0]) / \
            action.lateral().delta()
        self._velocity[0] -= \
            (self._velocity[0] - lateral_speed) / CAR_EXECUTION_DAMPING
        self._position[0] = self._position[0] + delta * self._velocity[0]

    @staticmethod
    def from_dict(
            spec,
    ):
        agent = None
        if spec['agent']['type'] == "adas":
            agent = ADAS.from_dict(spec['agent'])

        return Car(
            spec['id'],
            spec['position'],
            spec['shape'],
            spec['velocity'],
            agent,
        )
