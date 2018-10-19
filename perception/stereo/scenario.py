import cv2
import os

from utils.config import Config
from utils.log import Log
from utils.scenario import Scenario, ScenarioSpec


class StereoScenario(Scenario):
    def __init__(
            self,
            config: Config,
            spec: ScenarioSpec,
    ) -> None:
        super(StereoScenario, self).__init__(
            config,
            spec,
        )

        self._left = cv2.imread(
            os.path.join(
                os.path.dirname(spec.path()),
                spec.data()['left'],
            ),
        )
        self._right = cv2.imread(
            os.path.join(
                os.path.dirname(spec.path()),
                spec.data()['right'],
            ),
        )

    def run(
            self,
    ) -> bool:
        dump_path = os.path.join(self.dump_dir(), "dump.json")

        left_path = os.path.join(self.dump_dir(), "left.png")
        right_path = os.path.join(self.dump_dir(), "right.png")

        Log.out(
            "Dumping state", {
                'path': dump_path,
            })

        os.makedirs(self.dump_dir())

        cv2.imwrite(left_path, self._left)
        cv2.imwrite(right_path, self._right)

    def view(
            self,
    ) -> str:
        return self._config.get('utils_viewer_url') + \
            'scenarios/perception.stereo/' + self._id
