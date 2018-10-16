import typing

from state.entity import EntityType

from utils.config import Config


class BBox:
    def __init__(
            self,
            type: EntityType,
            confidence: float,
            position: typing.List[int],
            width: int,
            height: int,
    ) -> None:
        assert len(position) == 2
        assert 0.0 <= confidence and confidence <= 1.0

        self._type = type
        self._confidence = confidence
        self._position = position
        self._width = width
        self._height = height

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

    def width(
            self,
    ) -> int:
        return self._width

    def height(
            self,
    ) -> int:
        return self._height


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
