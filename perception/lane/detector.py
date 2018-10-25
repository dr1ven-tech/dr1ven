import typing

from utils.config import Config


class Lane:
    def __init__(
            self,
    ) -> None:
        pass


class LaneDetector:
    """ `LaneDetector` is the interface for generic lane detection.
    """
    def __init__(
            self,
            config: Config,
    ) -> None:
        pass

    def detect(
            self,
            image,
    ) -> typing.List[Lane]:
        raise Exception("Not implemented")
