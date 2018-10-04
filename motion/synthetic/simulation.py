import copy
import json
import os
import typing

from motion.synthetic.constants import FORWARD_ORIENTATION_FRONT_RANGE
# from motion.synthetic.constants import LATERAL_ORIENTATION_FRONT_RANGE
from motion.synthetic.constants import FORWARD_ORIENTATION_BACK_RANGE
# from motion.synthetic.constants import LATERAL_ORIENTATION_BACK_RANGE

from motion.synthetic.map import SyntheticMap
from motion.synthetic.entity import SyntheticEntity
from motion.synthetic.entity import ADASCar

from state.entity import Entity, EntityOccupation, EntityOrientation
from state.highway import Highway
from state.constants import HIGHWAY_LANE_DEPTH
from state.constants import EGO_POSITION_DEPTH

from utils.config import Config
from utils.log import Log
from utils.scenario import Scenario, ScenarioSpec


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

        def entity_state(e, ego):
            p = copy.deepcopy(e.position())
            p[1] -= start

            # If the entity is out of the vicinity of the ego vehicule, just
            # return None so that it will get filtererd out.
            if p[1] < 0 or p[1] >= HIGHWAY_LANE_DEPTH:
                return None

            if not ego and (p[1] - e.shape()[1] >
                            EGO_POSITION_DEPTH +
                            FORWARD_ORIENTATION_FRONT_RANGE):
                p[1] -= e.shape()[1]
                return Entity(
                    e.type(),
                    e.id(),
                    EntityOccupation(
                        EntityOrientation.FORWARD,
                        p,
                        e.shape()[0],
                        e.shape()[2],
                    ),
                    e.velocity(),
                )
            elif ego or (p[1] <
                         EGO_POSITION_DEPTH -
                         FORWARD_ORIENTATION_BACK_RANGE):
                return Entity(
                    e.type(),
                    e.id(),
                    EntityOccupation(
                        EntityOrientation.FORWARD,
                        p,
                        e.shape()[0],
                        e.shape()[2],
                    ),
                    e.velocity(),
                )
            else:
                # TODO(stan): handle lateral orientation
                return Entity(
                    e.type(),
                    e.id(),
                    EntityOccupation(
                        EntityOrientation.FORWARD,
                        p,
                        e.shape()[0],
                        e.shape()[2],
                    ),
                    e.velocity(),
                )

        sections = self._map.truncate(start, end)
        ego = entity_state(entity, True)
        entities = [
            entity_state(e, False)
            for e in self._entities if e.id() != entity.id()
        ]
        entities = [e for e in entities if e is not None]

        return Highway(
            sections,
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
            entity = None

            if e['type'] == 'adas_car':
                entity = ADASCar.from_dict(e)

            assert entity is not None
            entities.append(entity)

            if entity.id() == spec.data()['ego_id']:
                self._ego = entity
        assert self._ego is not None

        map_path = os.path.join(
            os.path.dirname(__file__),
            "maps",
            spec.data()['map'] + ".json",
        )

        self._simulation = Simulation(
            SyntheticMap.from_file(map_path),
            entities,
        )

    def run(
            self,
    ) -> bool:
        dump = {
            'delta': self._delta,
            'steps': []
        }

        for s in range(self._steps):
            self._simulation.step(s, self._delta)
            dump['steps'].append({
                'step': s,
                'state': dict(self._simulation.state(self._ego)),
            })

        dump_path = os.path.join(self.dump_dir(), "dump.json")

        Log.out(
            "Dumping Simulation state", {
                'path': dump_path,
            })

        os.makedirs(self.dump_dir())
        with open(dump_path, 'w') as out:
            json.dump(dump, out, indent=2)

        return True

    def view(
            self,
    ) -> str:
        return self._config.get('viewer_url') + \
            'scenarios/motion/synthetic/' + self._id
