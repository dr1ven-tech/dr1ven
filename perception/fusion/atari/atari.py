import math
import numpy as np
import random
import time
import typing

from perception.bbox.detector import BBox
from perception.bbox.yolov3.yolov3 import YOLOv3
from perception.lane.detector import Lane
from perception.lane.lanenet.lanenet import LaneNet

from state.constants import \
    HIGHWAY_LANE_DEPTH, HIGHWAY_LANE_WIDTH, EGO_POSITION_DEPTH, \
    HIGHWAY_VOXEL_WIDTH
from state.entity import Entity, EntityType
from state.entity import EntityOccupation, EntityOrientation
from state.highway import Highway
from state.section import Section, RoadType

from utils.config import Config
from utils.log import Log


class Atari:
    def __init__(
            self,
            config: Config,
            lane_count: int,
    ) -> None:
        self._lane_detector = LaneNet(config)
        self._bbox_detector = YOLOv3(config)
        self._lane_count = lane_count

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

        assert len(lanes) >= 2

        camera_center = front_camera.shape[1] / 2

        left = None
        right = None
        for l in lanes:
            if l.coordinates()[0][0] < camera_center and \
                    left is None:
                left = l
            if l.coordinates()[0][0] > camera_center and \
                    right is None:
                right = l

            if left and \
                    l.coordinates()[0][0] >= left.coordinates()[0][0] and \
                    l.coordinates()[0][0] < camera_center:
                left = l
            if right and \
                    l.coordinates()[0][0] <= right.coordinates()[0][0] and \
                    l.coordinates()[0][0] > camera_center:
                right = l

        assert left is not None
        assert right is not None

        ext_left = left
        for l in lanes:
            if l.coordinates()[0][0] < ext_left.coordinates()[0][0]:
                ext_left = l
        if ext_left == left:
            ext_left = None

        ext_right = right
        for l in lanes:
            if l.coordinates()[0][0] < ext_right.coordinates()[0][0]:
                ext_right = right
        if ext_right == l:
            ext_right = None

        # Default "Atari" environment for now (fixed `self._lane_count`). Note
        # that the current implementation does not know how to localize the ego
        # vehicle further than the 2 left-most lanes.
        section = Section(
            0, HIGHWAY_LANE_DEPTH-1,
            [RoadType.DRIVABLE] * (HIGHWAY_LANE_WIDTH * self._lane_count) +
            [RoadType.EMERGENCY] * (HIGHWAY_LANE_WIDTH-1) +
            [RoadType.INVALID],
        )

        # TODO(stan): The fuser should be passed as argument a `Vehicle` object
        # containing a list of sensor and their positions (eg `Camera`,
        # `Radar`, ...). The inputs used by the fuser should be tied to the
        # sensor that produced them to retrieve its pose (eg. `CameraImage`).

        # For now we'll take pretty arbitrary constants.
        REAL_LANE_WIDTH = 3.5
        VEHICLE_WIDTH = 1.8
        VEHICLE_HEIGHT = 1.5
        CAMERA_LATERAL_POSITION = 0.2

        lateral_lane_position = (
            (camera_center - left.coordinates()[0][0]) /
            (right.coordinates()[0][0] - left.coordinates()[0][0])
        ) * REAL_LANE_WIDTH - CAMERA_LATERAL_POSITION

        # TODO(stan): be capable of locating the vehicle further than the 2
        # left-most lanes.
        lane_index = 0
        if ext_left is not None:
            lane_index = 1

        # TODO(stan): We don't have odomoter recordings for now, os let's
        # assume the spped to be constant for the ego vehicle. (50 voxel/s is
        # 90 km/h).

        # TODO(stan): track lateral speed of ego vehicle.
        ego = Entity(
            EntityType.CAR,
            'ego',
            EntityOccupation(
                EntityOrientation.FORWARD,
                [
                    HIGHWAY_LANE_WIDTH * lane_index +
                    int(math.floor(
                        lateral_lane_position / HIGHWAY_VOXEL_WIDTH
                    )),
                    EGO_POSITION_DEPTH,
                    0.0,
                ],
                int(math.floor(VEHICLE_WIDTH / HIGHWAY_VOXEL_WIDTH)),
                int(math.floor(VEHICLE_HEIGHT / HIGHWAY_VOXEL_WIDTH)),
            ),
            [0.0, 50.0, 0.0],
        )

        # TODO(stan): track vehicles across frames, in particular their speed.
        entities = []
        for b in boxes:
            box_bottom_height = b.position()[1] + b.shape()[1]

            l = left.at_height(box_bottom_height)
            r = right.at_height(box_bottom_height)

            assert r[0] > l[0]

            real_width = b.shape()[0] / (r[0]-l[0]) * REAL_LANE_WIDTH
            real_height = b.shape()[1] / b.shape()[0] * real_height

            # z / f = DX / dx
            distance =

            entities.append(
                Entity(
                    b.type(),
                    "{}".format(random.randrange(99999)),
                    EntityOccupation(
                        EntityOrientation.FORWARD,
                        [
                        ],
                    ),
                    [0.0, 50.0, 0.0],
                )
            )

        import pdb; pdb.set_trace()

        return Highway([section], ego, []), boxes, lanes
