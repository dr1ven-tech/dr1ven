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
            step: int,
            delta: float,
    ):
        for e in self._entities:
            e.step(step, delta)

    def state(
            self,
            entity: Entity,
    ) -> Highway:
        """ `state` returns the current `state.Highway` for an entity.

        The state is computed from the "point of view" of the entity passed as
        argument (impacts depth position).
        """
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
        self._delta = spec.data()['delta']
        self._steps = spec.data()['steps']

        entities = []
        for e in spec.data()['entities']:
            if e['type'] == 'adas_car':
                entities.append(ADASCar.from_dict(e))

        map_path = os.path.join(
            os.path.dirname(__file__),
            "maps",
            spec.data()['map'] + '.json',
        )

        self._simulation = Simulation(
            Map.from_file(map_path),
            entities,
        )

    def run(
            self,
    ) -> bool:
        # TODO(stan): initiate dump_dir
        for s in range(self._steps):
            self._simulation.step(s, self._delta)
            # TODO(stan): build state
        # TODO(stan): dump state

    def view(
            self,
    ) -> str:
        return self._config('scenarios_viewer_url') + \
            '/motion/synthetic/simulation/' + self._id
