import typing

from sensors.camera import CameraImage

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
        assert len(coordinates) > 2
        self._coordinates = reversed(sorted(coordinates, key=lambda p: p[1]))

    def coordinates(
            self,
    ) -> typing.List[typing.List[int]]:
        return self._coordinates

    def at_height(
            self,
            height: int,
    ) -> typing.List[int]:
        maximal = 0
        for i in range(len(self._coordinates)):
            maximal = i
            if (self._coordinates[1] > height):
                break

        neighbors = []
        if maximal == len(self._coordinates)-1:
            neighbors = [
                self._coordinates[-2], self._coordinates[-1]
            ]
        else:
            neighbors = [
                self._coordinates[maximal], self._coordinates[maximal+1]
            ]

        assert neighbors[0][1] != neighbors[1][1]

        alpha = (neighbors[1][0] - neighbors[0][0]) / \
            (neighbors[0][1] != neighbors[1][1])

        return [neighbors[0][0] + alpha * (neighbors[0][0] - height), height]

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
            image: CameraImage,
    ) -> typing.List[Lane]:
        raise Exception("Not implemented")
