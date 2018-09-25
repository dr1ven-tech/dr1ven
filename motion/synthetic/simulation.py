import typing

from motion.synthetic.map import Map
from motion.synthetic.entity import Entity
from motion.agent import Agent

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
        # step entities
        # check for collisions
        pass
