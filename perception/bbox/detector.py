import typing

from state.entity import EntityType

from utils.config import Config
from utils.scenario import Scenario, ScenarioSpec


class BBox:
    def __init__(
            self,
            type: EntityType,
            confidence: float,
            position: typing.List[int],
            shape: typing.List[int],
    ) -> None:
        assert len(position) == 2
        assert len(shape) == 2
        assert 0.0 <= confidence and confidence <= 1.0

        self._type = type
        self._confidence = confidence
        self._position = position
        self._shape = shape

    def type(
            self,
    ) -> EntityType:
        return self._type

    def confidence(
            self,
    ) -> float:
        return self._confidence

    def position(
            self,
    ) -> typing.List[int]:
        return self._position

    def shape(
            self,
    ) -> int:
        return self._shape

    @staticmethod
    def from_dict(
            spec,
    ):
        return BBox(
            EntityType(spec['type']),
            spec['confidence'],
            spec['position'],
            spec['shape'],
        )


class BBoxDetector:
    """ `Detector` is the interface for generic bounding box detection.

    Instantiating a detector might be a lengthy process as we're probably
    loading some pre-trained weights, etc...
    """
    def __init__(
            self,
            config: Config,
    ) -> None:
        pass

    def detect(
            self,
            image,
    ) -> typing.List[BBox]:
        raise Exception("Not implemented")


class BBoxDetectorScenario(Scenario):
    def __init__(
            self,
            config: Config,
            spec: ScenarioSpec,
    ) -> None:
        super(BBoxDetectorScenario, self).__init__(
            config,
            spec,
        )

    def run(
            self,
    ) -> bool:
        return True

    def view(
            self,
    ) -> str:
        return self._config.get('utils_viewer_url') + \
            'scenarios/perception.bbox.detector/' + self._id
