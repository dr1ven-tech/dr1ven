import cv2
import json
import numpy as np
import os

from perception.lane.lanenet.lanenet import LaneNet

from sensors.camera import Camera, CameraImage

from utils.config import Config
from utils.log import Log
from utils.scenario import Scenario, ScenarioSpec


class LaneScenario(Scenario):
    def __init__(
            self,
            config: Config,
            spec: ScenarioSpec,
    ) -> None:
        super(LaneScenario, self).__init__(
            config,
            spec,
        )

        Log.out(
            "Initializing detector", {
                'detector': spec.data()['detector'],
            })

        if spec.data()['detector'] == 'lanenet':
            self._detector = LaneNet(config)

        camera = Camera.from_dict(spec.data()['camera'])

        self._image = CameraImage.from_path_and_camera(
            os.path.join(
                os.path.dirname(spec.path()),
                spec.data()['image'],
            ),
            camera,
        )

    def run(
            self,
    ) -> bool:
        lanes, points, fitted = self._detector.detect(self._image)

        dump = {
            'detected': [dict(l) for l in lanes],
        }

        # assert len(lanes) > 1

        # TODO(stan): test criteria

        bird_eye = self._image.bird_eye_data()
        for p in points:
            bird_eye = cv2.rectangle(
                bird_eye,
                tuple(np.int64(p-np.array([1, 1]))),
                tuple(np.int64(p+np.array([1, 1]))),
                (0, 255, 0), 1,
            )
        for p in fitted:
            bird_eye = cv2.rectangle(
                bird_eye,
                tuple(np.int64(p-np.array([1, 1]))),
                tuple(np.int64(p+np.array([1, 1]))),
                (0, 0, 255), 1,
            )

        dump_path = os.path.join(self.dump_dir(), "dump.json")
        image_path = os.path.join(self.dump_dir(), "image.png")
        bird_eye_path = os.path.join(self.dump_dir(), "bird_eye.png")

        Log.out(
            "Dumping detection", {
                'path': dump_path,
            })

        os.makedirs(self.dump_dir())
        with open(dump_path, 'w') as out:
            json.dump(dump, out, indent=2)

        cv2.imwrite(image_path, self._image.data())
        cv2.imwrite(bird_eye_path, bird_eye)

        self._detector.close()

        return True

    def view(
            self,
    ) -> str:
        return self._config.get('utils_viewer_url') + \
            'scenarios/perception.lane/' + self._id
