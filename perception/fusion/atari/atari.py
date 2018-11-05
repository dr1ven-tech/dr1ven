import math
import random
import time
import typing

from perception.bbox.detector import BBox
from perception.bbox.yolov3.yolov3 import YOLOv3
from perception.lane.detector import Lane
from perception.lane.lanenet.lanenet import LaneNet

from sensors.camera import CameraImage

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
            front_camera: CameraImage,
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
        lanes = sorted(lanes, key=lambda l: l.coordinates()[-1][0])

        # Default "Atari" environment for now (fixed `self._lane_count`).
        section = Section(
            0, HIGHWAY_LANE_DEPTH-1,
            [RoadType.INVALID] * HIGHWAY_LANE_WIDTH +
            [RoadType.DRIVABLE] * (HIGHWAY_LANE_WIDTH * self._lane_count) +
            [RoadType.EMERGENCY] * (HIGHWAY_LANE_WIDTH-1) +
            [RoadType.INVALID],
        )

        camera_center = front_camera.size()[0] / 2

        lane_index, lateral_lane_position, _, _, _, _ = self._lane_position(
            lanes, camera_center, lanes[0].coordinates()[-1][1],
        )

        # TODO(stan): The fuser should be passed as argument a `Vehicle` object
        # containing a list of sensor and their positions (eg `Camera`,
        # `Radar`, ...) as well as the vehicle dimensions.

        # For now we'll take pretty arbitrary constants.
        VEHICLE_WIDTH = 1.8
        VEHICLE_HEIGHT = 1.5
        CAMERA_LATERAL_POSITION = 0.2

        # Readjust the lateral_lane_positon based on the camera position.
        lateral_lane_position -= CAMERA_LATERAL_POSITION
        if lateral_lane_position < 0:
            assert lane_index > 0
            lane_index -= 1
            lateral_lane_position += HIGHWAY_VOXEL_WIDTH * HIGHWAY_LANE_WIDTH

        # TODO(stan): We don't have odomoter recordings for now, os let's
        # assume the speed to be constant for the ego vehicle. (50 voxel/s is
        # 90 km/h).

        # TODO(stan): track lateral speed of ego vehicle.
        ego = Entity(
            EntityType.CAR,
            'ego',
            EntityOccupation(
                EntityOrientation.FORWARD,
                [
                    HIGHWAY_LANE_WIDTH * (lane_index + 1) +
                    int(math.floor(
                        lateral_lane_position / HIGHWAY_VOXEL_WIDTH
                    )),
                    EGO_POSITION_DEPTH,
                    0.0,
                ],
                int(math.ceil(VEHICLE_WIDTH / HIGHWAY_VOXEL_WIDTH)),
                int(math.ceil(VEHICLE_HEIGHT / HIGHWAY_VOXEL_WIDTH)),
            ),
            [0.0, 50.0, 0.0],
        )

        Log.out(
            "Detected ego", {
                'lateral_index': (lane_index + 1),
                'lateral_lane_positon': lateral_lane_position,
            })

        # TODO(stan): track vehicles across frames, in particular their speed.
        entities = []
        for b in boxes:
            box_bottom_height = b.position()[1] + b.shape()[1]
            box_left_width = b.position()[0]
            box_right_width = b.position()[0] + b.shape()[0]

            if box_right_width < lanes[0].at_height(box_bottom_height)[0] or \
                    box_left_width > lanes[-1].at_height(box_bottom_height)[0]:
                Log.out(
                    "Entity out of bound", {
                        'box_left_width': box_left_width,
                        'box_right_width': box_right_width,
                        'box_bottom_height': box_bottom_height,
                    })
                continue

            lane_index, lateral_lane_position, \
                left_lanes, right_lanes, \
                left_at_height, right_at_height = \
                self._lane_position(lanes, b.position()[0], box_bottom_height)

            real_width = b.shape()[0] / \
                (right_at_height[0]-left_at_height[0]) * \
                (HIGHWAY_VOXEL_WIDTH * HIGHWAY_LANE_WIDTH)
            real_height = b.shape()[1] / b.shape()[0] * real_width

            # `z = f * DX / dx`. We use the lanes to estimate distance as they
            # are not subject to occlusion.
            distance = front_camera.camera().camera_matrix()[0][0] * \
                (HIGHWAY_VOXEL_WIDTH * HIGHWAY_LANE_WIDTH) / \
                (right_at_height[0]-left_at_height[0])

            Log.out(
                "Detected entity", {
                    'type': b.type(),
                    'box_left_width': box_left_width,
                    'box_bottom_height': box_bottom_height,
                    'lateral_index': (lane_index + 1),
                    'lateral_lane_positon': lateral_lane_position,
                    'distance': distance,
                    'width': real_width,
                    'height': real_height,
                })

            entities.append(
                Entity(
                    b.type(),
                    "{}".format(random.randrange(99999)),
                    EntityOccupation(
                        EntityOrientation.FORWARD,
                        [
                            HIGHWAY_LANE_WIDTH * (lane_index + 1) +
                            int(math.floor(
                                lateral_lane_position / HIGHWAY_VOXEL_WIDTH
                            )),
                            EGO_POSITION_DEPTH +
                            int(math.floor(distance / HIGHWAY_VOXEL_WIDTH)),
                            0.0,
                        ],
                        int(math.ceil(real_width / HIGHWAY_VOXEL_WIDTH)),
                        int(math.ceil(real_height / HIGHWAY_VOXEL_WIDTH)),
                    ),
                    [0.0, 50.0, 0.0],
                )
            )

        return Highway([section], ego, entities), boxes, lanes

    @staticmethod
    def _lane_position(
            lanes: typing.List[Lane],
            width: int,
            height: int,
    ) -> (int, float):
        split = -1
        for i in range(len(lanes)):
            if lanes[i].at_height(height)[0] <= width:
                split = i
            else:
                break

        left_lanes = list(reversed(lanes[:split+1]))
        right_lanes = lanes[split+1:]

        lane_index = len(left_lanes)-1

        if len(left_lanes) == 0:
            left = right_lanes[0]
            right = right_lanes[1]
        elif len(right_lanes) == 0:
            left = left_lanes[-2]
            right = left_lanes[-1]
        else:
            left = left_lanes[0]
            right = right_lanes[0]

        right_at_height = right.at_height(height)
        left_at_height = left.at_height(height)

        assert right_at_height[0] > left_at_height[0]

        # Log.out("DEBUG _lane_position", {
        #     'height': height,
        #     'width': width,
        #     'left_at_height[0]': left_at_height[0],
        #     'right_at_height_width[0]': right_at_height[0],
        # })
        lateral_lane_position = (
            (width - left_at_height[0]) /
            (right_at_height[0] - left_at_height[0])
        ) * (HIGHWAY_VOXEL_WIDTH * HIGHWAY_LANE_WIDTH)

        if len(left_lanes) == 0:
            lateral_lane_position += HIGHWAY_VOXEL_WIDTH * HIGHWAY_LANE_WIDTH
        if len(right_lanes) == 0:
            lane_index += 1
            lateral_lane_position -= HIGHWAY_VOXEL_WIDTH * HIGHWAY_LANE_WIDTH

        return lane_index, lateral_lane_position, \
            left_lanes, right_lanes, \
            left_at_height, right_at_height
