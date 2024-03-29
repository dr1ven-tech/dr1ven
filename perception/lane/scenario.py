import cv2
import json
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
        lanes = self._detector.detect(self._image)

        dump = {
            'detected': [dict(l) for l in lanes],
        }

        assert len(lanes) > 1

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

        cv2.imwrite(image_path, self._image.data())

        self._detector.close()

        return True

    def view(
            self,
    ) -> str:
        return self._config.get('utils_viewer_url') + \
            'scenarios/perception.lane/' + self._id
