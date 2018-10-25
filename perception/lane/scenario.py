import cv2
import json
import os

from perception.lane.detector import Lane
from perception.lane.lanenet.lanenet import LaneNet

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

        self._image = cv2.imread(
            os.path.join(
                os.path.dirname(spec.path()),
                spec.data()['image'],
            ),
        )

    def run(
            self,
    ) -> bool:
        resized = cv2.resize(
            self._image, (512, 256), interpolation=cv2.INTER_LINEAR,
        )

        mask = self._detector.detect(self._image)

        dump = {
            # 'detected': [dict(b) for b in boxes],
        }

        # TODO(stan): test criteria

        dump_path = os.path.join(self.dump_dir(), "dump.json")
        input_path = os.path.join(self.dump_dir(), "input.png")
        resized_path = os.path.join(self.dump_dir(), "resized.png")
        mask_path = os.path.join(self.dump_dir(), "mask.png")

        Log.out(
            "Dumping detection", {
                'path': dump_path,
            })

        os.makedirs(self.dump_dir())
        with open(dump_path, 'w') as out:
            json.dump(dump, out, indent=2)

        cv2.imwrite(input_path, self._image)
        cv2.imwrite(resized_path, resized)
        cv2.imwrite(mask_path, mask)

        return True

    def view(
            self,
    ) -> str:
        return self._config.get('utils_viewer_url') + \
            'scenarios/perception.lane/' + self._id
