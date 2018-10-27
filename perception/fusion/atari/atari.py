import numpy as np
import time
import typing

from perception.bbox.detector import BBox
from perception.bbox.yolov3.yolov3 import YOLOv3
from perception.lane.detector import Lane
from perception.lane.lanenet.lanenet import LaneNet

from state.highway import Highway

from utils.config import Config
from utils.log import Log


class Atari:
    def __init__(
            self,
            config: Config,
    ) -> None:
        self._lane_detector = LaneNet(config)
        self._bbox_detector = YOLOv3(config)

    def fuse(
            self,
            now: float,
            front_camera: np.ndarray,
    ) -> (Highway, typing.List[BBox], typing.List[Lane]):
        start = time.time()
        boxes = self._bbox_detector.detect(front_camera)
        Log.out(
            "Boxes detected", {
                'now': "{:.3f}".format(now),
                'count': len(boxes),
                'processing_time': (time.time() - start),
            })

        start = time.time()
        lanes = self._lane_detector.detect(front_camera)
        Log.out(
            "Lanes detected", {
                'now': "{:.3f}".format(now),
                'count': len(lanes),
                'processing_time': (time.time() - start),
            })

        return None, boxes, lanes
