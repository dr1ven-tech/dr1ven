import cv2
import json
import os

from perception.bbox.yolov3.yolov3 import YOLOv3

from utils.config import Config
from utils.log import Log
from utils.scenario import Scenario, ScenarioSpec

from sensors.camera import Camera, CameraImage


class BBoxScenario(Scenario):
    def __init__(
            self,
            config: Config,
            spec: ScenarioSpec,
    ) -> None:
        super(BBoxScenario, self).__init__(
            config,
            spec,
        )

        Log.out(
            "Initializing detector", {
                'detector': spec.data()['detector'],
            })

        if spec.data()['detector'] == 'yolov3':
            self._detector = YOLOv3(config)

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
        boxes = self._detector.detect(self._image, (640, 360))

        dump = {
            'detected': [dict(b) for b in boxes],
        }

        # TODO(stan): test criteria

        dump_path = os.path.join(self.dump_dir(), "dump.json")
        image_path = os.path.join(self.dump_dir(), "image.png")

        Log.out(
            "Dumping detection", {
                'path': dump_path,
            })

        os.makedirs(self.dump_dir())
        with open(dump_path, 'w') as out:
            json.dump(dump, out, indent=2)

        cv2.imwrite(image_path, self._image.data(size=(640, 360)))

        self._detector.close()

        return True

    def view(
            self,
    ) -> str:
        return self._config.get('utils_viewer_url') + \
            'scenarios/perception.bbox/' + self._id
