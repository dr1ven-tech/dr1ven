import typing

from utils.config import Config


class Lane:
    """ `Lane` represents a detected in an image.

    Detected lanes are represented as a list of coordinates describing a curve.
    The coordinates are orderd by increasing height in the source image.

    Even if most algorithm use polynomial fitting, they also reproject the
    fitted curve into the original image forcing the use of a list of
    coordinates instead of polynomial parameters.
    """
    def __init__(
            self,
            coordinates: typing.List[typing.List[int]]
    ) -> None:
        for p in coordinates:
            assert len(p) == 2
        self._coordinates = coordinates

    def coordinates(
            self,
    ) -> typing.List[typing.List[int]]:
        return self._coordinates

    def __iter__(
            self,
    ):
        yield 'coordinates', self._coordinates

    @staticmethod
    def from_dict(
            spec,
    ):
        return Lane(
            spec['coordinates'],
        )


class LaneDetector:
    """ `LaneDetector` is the interface for generic lane detection.

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
            image,
    ) -> typing.List[Lane]:
        raise Exception("Not implemented")
