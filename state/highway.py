import numpy as np

_voxel_none_road_type = 'none'
_voxel_road_types = [
    'drivable',
    'emergency',
    'parking',
]

_voxel_none_line_type = 'none'
_voxel_line_types = [
    'continuous',
    'dashed',
    'dense_dashed',
]

_voxel_none_object_type = 'none'
_voxel_object_types = [
    'ego',
    'unknown',
    'car',
    'truck',
    'motorbike',
    'traffic_cone',
    'safety_sign',
    'human',
    'animal',
]

_voxel_width = 0.5

class Voxel:
    def __init__(
            self,
            road_type,
            left_line_type,
            right_line_type,
            object_type,
            object_forward_speed,
            object_lateral_speed,
            object_vertical_speed,
    ):
        self.road_type = road_type
        self.line_types = [left_line_type, right_line_type]
        self.object_type = object_type
        self.object_speed = [
            object_forward_speed,
            object_lateral_speed,
            object_vertical_speed,
        ]

        assert self.road_type in (_voxel_road_types + [_voxel_none_road_type])
        assert self.line_types[0] in (_voxel_line_types + [_voxel_none_line_type])
        assert self.line_types[1] in (_voxel_line_types + [_voxel_none_line_type])
        assert self.object_type in (_voxel_object_types + [_voxel_none_object_type])

class Highway:
    def __init__(
            self,
    ):
        # (1000m x 3.5m x 5m).
        self._voxels = np.zeros((
            8,                        # 8 lanes
            2000, 7, 10,              # front, lateral, height (orthonormal)
            len(_voxel_road_types) +     # [mapping] road type
            2 * len(_voxel_line_types) + # [mapping] left/right line type
            len(_voxel_object_types) +   # [perception] object type
            3,                           # [perception] object speed
        ))

    def add_component(
            component,
    ):
        self._voxels += component

    def voxel(
            self,
            lane,
            depth,
            left,
            top,
    ):
        v = self._voxels[lane, depth, left, top]

        i = 0

        road_type = _voxel_none_road_type
        if len(np.nonzero(v[i:i+len(_voxel_road_types)])[0]) > 0:
            assert len(np.nonzero(v[i:i+len(_voxel_road_types)])[0]) == 1
            road_type = _voxel_road_types[
                np.nonzero(v[i:i+len(_voxel_road_types)])[0][0]
            ]
        i += len(_voxel_road_types)

        left_line_type = _voxel_none_line_type
        if len(np.nonzero(v[i:i+len(_voxel_line_types)])[0]) > 0:
            assert len(np.nonzero(v[i:i+len(_voxel_line_types)])[0]) == 1
            left_line_type = _voxel_line_types[
                np.nonzero(v[i:i+len(_voxel_line_types)])[0][0]
            ]
        i += len(_voxel_line_types)

        right_line_type = _voxel_none_line_type
        if len(np.nonzero(v[i:i+len(_voxel_line_types)])[0]) > 0:
            assert len(np.nonzero(v[i:i+len(_voxel_line_types)])[0]) == 1
            right_line_type = _voxel_line_types[
                np.nonzero(v[i:i+len(_voxel_line_types)])[0][0]
            ]
        i += len(_voxel_line_types)

        object_type = _voxel_none_object_type
        if len(np.nonzero(v[i:i+len(_voxel_object_types)])[0]) > 0:
            assert len(np.nonzero(v[i:i+len(_voxel_object_types)])[0]) == 1
            object_type = _voxel_object_types[
                np.nonzero(v[i:i+len(_voxel_object_types)])[0][0]
            ]
        i += len(_voxel_object_types)

        speeds = v[i:i+3]

        return Voxel(
            road_type,
            left_line_type,
            left_line_type,
            object_type,
            speeds[0],
            speeds[1],
            speeds[2],
        )

if __name__ == "__main__":
    r = Highway()
    v = r.voxel(0, 0, 0, 0)

