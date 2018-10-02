import copy
import os
import typing

from motion.synthetic.map import SyntheticMap
from motion.synthetic.entity import SyntheticEntity
from motion.synthetic.entity import ADASCar

from state.entity import Entity, EntityOccupation, EntityOrientation
from state.highway import Highway
from state.constants import HIGHWAY_LANE_DEPTH
from state.constants import EGO_POSITION_DEPTH

from scenarios.scenario import Scenario
from scenarios.scenario import ScenarioSpec

from utils.config import Config


class Simulation:
    def __init__(
            self,
            map: SyntheticMap,
            entities: typing.List[SyntheticEntity]
    ) -> None:
        self._map = map
        self._entities = entities

    def entities(
            self,
    ) -> typing.List[SyntheticEntity]:
        return self._entities

    def map(
            self,
    ) -> SyntheticMap:
        return self._map

    def step(
            self,
            step: int,
            delta: float,
    ):
        for e in self._entities:
            e.step(step, delta, self.state(e))

    def state(
            self,
            entity: SyntheticEntity,
    ) -> Highway:
        """ `state` returns the current `state.Highway` for an entity.

        The state is computed from the "point of view" of the entity passed as
        argument (impacts depth position).
        """
        start = entity.position()[1]-EGO_POSITION_DEPTH
        end = entity.position()[1]-EGO_POSITION_DEPTH+HIGHWAY_LANE_DEPTH-1

        def entity_state(e):
            p = copy.copy(e.position())
            p[1] -= start

            return Entity(
                e.type(),
                e.id(),
                EntityOccupation(
                    EntityOrientation.FORWARD,
                    e.lane(),
                    p,
                    e.shape()[0],
                    e.shape()[2],
                ),
                e.velocity(),
            )

        lanes = self._map.truncate(start, end)
        ego = entity_state(entity)
        entities = [
            entity_state(e)
            for e in self._entities if e.id() != entity.id()
        ]

        return Highway(
            lanes,
            ego,
            entities,
        )


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
            SyntheticMap.from_file(map_path),
            entities,
        )

    def run(
            self,
    ) -> bool:
        # TODO(stan): initiate dump_dir
        for s in range(self._steps):
            self._simulation.step(s, self._delta)
            # TODO(stan): dump state

        return True

    def view(
            self,
    ) -> str:
        return self._config.get('scenarios_viewer_url') + \
            '/motion/synthetic/simulation/' + self._id
