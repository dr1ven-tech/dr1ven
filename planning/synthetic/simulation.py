import json
import os
import typing

from planning.synthetic.constants import FORWARD_ORIENTATION_FRONT_RANGE
from planning.synthetic.constants import FORWARD_ORIENTATION_BACK_RANGE

from planning.synthetic.map import SyntheticMap
from planning.synthetic.entity import SyntheticEntity
from planning.synthetic.entities.car import Car

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
        for e in entities:
            assert e.position()[0] < map.width()

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
        start = int(entity.position()[1]) - EGO_POSITION_DEPTH
        end = int(entity.position()[1]) - \
            EGO_POSITION_DEPTH+HIGHWAY_LANE_DEPTH-1

        def entity_state(
                e: SyntheticEntity,
                ego: bool,
        ):
            position = [int(p) for p in e.position()]
            shape = [int(s) for s in e.shape()]

            position[1] -= start

            # If the entity is out of the vicinity of the ego vehicule, just
            # return None so that it will get filtererd out.
            if position[1] < 0 or position[1] >= HIGHWAY_LANE_DEPTH:
                return None

            if not ego and (position[1] - shape[1] >
                            EGO_POSITION_DEPTH +
                            FORWARD_ORIENTATION_FRONT_RANGE):
                position[1] -= shape[1]
                return Entity(
                    e.type(),
                    e.id(),
                    EntityOccupation(
                        EntityOrientation.FORWARD,
                        position,
                        shape[0],
                        shape[2]
                    ),
                    e.velocity(),
                )
            elif ego or (position[1] <
                         EGO_POSITION_DEPTH -
                         FORWARD_ORIENTATION_BACK_RANGE):
                return Entity(
                    e.type(),
                    e.id(),
                    EntityOccupation(
                        EntityOrientation.FORWARD,
                        position,
                        shape[0],
                        shape[2],
                    ),
                    e.velocity(),
                )
            else:
                # If the entity is on the left of the reference entity, Place
                # the lateral occupation on the right-hand face of the entity.
                if position[0] + shape[0] <= int(entity.position()[0]):
                    position[0] += shape[0]
                # The occupation is positioned at the back of the entity.
                position[1] -= shape[1]

                # TODO(stan): for now we have a perfect coverage of the entity
                # laterally which may not be true eventually.
                return Entity(
                    e.type(),
                    e.id(),
                    EntityOccupation(
                        EntityOrientation.LATERAL,
                        position,
                        shape[1],
                        shape[2],
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

            if e['type'] == "car":
                entity = Car.from_dict(e)

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

        outcome = True

        for s in range(self._steps):
            self._simulation.step(s, self._delta)
            dump['steps'].append({
                'step': s,
                'state': dict(self._simulation.state(self._ego)),
            })
            for e in self._simulation.entities():
                if e.id() != self._ego.id() and self._ego.collide(e):
                    Log.out(
                        "Collision detected", {
                            'ego': self._ego.id(),
                            'other': e.id(),
                        })
                    outcome = False
            if not outcome:
                break

        dump_path = os.path.join(self.dump_dir(), "dump.json")

        Log.out(
            "Dumping Simulation state", {
                'path': dump_path,
            })

        os.makedirs(self.dump_dir())
        with open(dump_path, 'w') as out:
            json.dump(dump, out, indent=2)

        return outcome

    def view(
            self,
    ) -> str:
        return self._config.get('utils_viewer_url') + \
            'scenarios/planning.synthetic/' + self._id
