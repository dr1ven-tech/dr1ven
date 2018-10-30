import typing

from sensors.camera import CameraImage

from state.entity import EntityType

from utils.config import Config


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
    ) -> typing.List[int]:
        return self._shape

    def __iter__(
            self,
    ):
        yield 'type', self._type.value
        yield 'confidence', self._confidence
        yield 'position', self._position
        yield 'shape', self._shape

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
    """ `BBoxDetector` is the interface for generic bounding box detection.

    Instantiating a detector might be a lengthy process as we're probably
    loading some pre-trained weights, etc...
    """
    def __init__(
            self,
            config: Config,
    ) -> None:
        self._closed = False

    def close(
            self,
    ) -> None:
        self._closed = True

    def detect(
            self,
            image: CameraImage,
            size: typing.Optional[typing.Tuple[int, int]] = None,
    ) -> typing.List[BBox]:
        raise Exception("Not implemented")
