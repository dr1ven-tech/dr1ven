import cv2
import json
import os

from perception.bbox.detector import BBox
from perception.bbox.yolov3.yolov3 import YOLOv3

from utils.config import Config
from utils.log import Log
from utils.scenario import Scenario, ScenarioSpec


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

        self._ground_truth = []
        for b in spec.data()['ground_truth']:
            self._ground_truth.append(BBox.from_dict(b))

        Log.out(
            "Initializing detector", {
                'detector': spec.data()['detector'],
            })

        if spec.data()['detector'] == 'yolov3':
            self._detector = YOLOv3(config)

        self._image = cv2.imread(
            os.path.join(
                os.path.dirname(spec.path()),
                spec.data()['image'],
            ),
        )

    def run(
            self,
    ) -> bool:
        boxes = self._detector.detect(self._image)

        dump = {
            'ground_truth': [dict(b) for b in self._ground_truth],
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

        cv2.imwrite(image_path, self._image)

        return True

    def view(
            self,
    ) -> str:
        return self._config.get('utils_viewer_url') + \
            'scenarios/perception.bbox/' + self._id
