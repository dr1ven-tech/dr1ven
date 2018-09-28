import os
import typing

from motion.synthetic.map import Map
from motion.synthetic.entity import Entity
from motion.synthetic.entity import ADASCar
from motion.agent import Agent

from state.highway import Highway

from scenarios.scenario import Scenario
from scenarios.scenario import ScenarioSpec

from utils.config import Config

class Simulation:
    def __init__(
            self,
            map: Map,
            entities: typing.List[Entity]
    ) -> None:
        self._map = map
        self._entities = entities

    def step(
            self,
            delta: float,
    ):
        pass

    def state(
            self,
    ) -> Highway:
        pass

class SimulationScenario(Scenario):
    def __init__(
            self,
            config: Config,
            spec: ScenarioSpec,
    ) -> None:
        super(SimulationScenario, self).__init__(
            config,
            spec,
        )

        entities = []
        for e in spec.data()['entities']:
            if e['type'] == 'adas_car':
                entities.append(ADASCar.from_dict(e))

        self._simulation = Simulation(
            None,
            entities,
        )

    def run(
            self,
    ) -> bool:
        pass

    def view(
            self,
    ) -> str:
        return self._config('scenarios_viewer_url') + \
            '/motion/synthetic/simulation/' + self._id
