import cv2
import numpy as np
import typing


class Camera:
    """ `Camera` represents a camera sensor.

    It stores the intrinsic parameters of the camera under `camera_matrix` as
    well as a `bird_eye_projection`.
    """
    def __init__(
            self,
            camera_matrix: np.ndarray,
            bird_eye_projection: np.ndarray,
    ) -> None:
        assert camera_matrix.shape == (3, 3)
        assert bird_eye_projection.shape == (3, 3)

        self._camera_matrix = camera_matrix
        self._bird_eye_projection = bird_eye_projection

    def camera_matrix(
            self,
    ) -> np.ndarray:
        return self._camera_matrix

    def bird_eye_projection(
            self,
    ) -> np.ndarray:
        return self._bird_eye_projection

    def __iter__(
            self,
    ):
        yield 'camera_matrix', self._camera_matrix.tolist()
        yield 'bird_eye_projection', self.bird_eye_projection.tolist()

    @staticmethod
    def from_dict(
            spec,
    ):
        return Camera(
            np.array(spec['camera_matrix']),
            np.array(spec['bird_eye_projection']),
        )


class CameraImage:
    """ `CameraImage` represents an image produced by a `Camera` sensor.

    It includes the image data stored as numpy ndarray processable with opencv
    as well as a reference to the `Camera` sensor that produced it.
    """
    def __init__(
            self,
            camera: Camera,
            data: np.ndarray,
    ) -> None:
        assert len(data.shape) == 3

        self._camera = camera
        self._data = data

    def camera(
            self,
    ) -> Camera:
        return self._camera

    def data(
            self,
            size: typing.Optional[typing.Tuple[int, int]] = None,
    ) -> np.ndarray:
        """ `data` returns the raw image data.

        It accepts an optional size parameter to return a scaled version of the
        raw image data as numpy ndarray.
        """
        if size is None:
            return self._data
        else:
            # TODO(stan): eventually cache the resized images.
            return cv2.resize(
                self._data, size, interpolation=cv2.INTER_LINEAR,
            )

    def size(
            self,
    ) -> typing.Tuple[int, int]:
        return (self._data.shape[1], self._data.shape[0])

    @staticmethod
    def from_path_and_camera(
            path: str,
            camera: Camera,
    ):
        data = cv2.imread(path)

        return CameraImage(
            camera,
            data,
        )
