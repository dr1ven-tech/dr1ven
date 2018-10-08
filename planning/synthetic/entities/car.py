import typing

from state.highway import Highway
from state.entity import EntityType
from planning.agent import Agent
from planning.agents.adas import ADAS
from planning.synthetic.entity import SyntheticEntity


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

        self._agent = Agent

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
        pass

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
