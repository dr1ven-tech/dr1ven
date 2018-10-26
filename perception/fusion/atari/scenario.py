import cv2
import json
import os

from perception.fusion.atari.fuser import AtariFuser

from utils.config import Config
from utils.log import Log
from utils.scenario import Scenario, ScenarioSpec


class AtariScenario(Scenario):
    def __init__(
            self,
            config: Config,
            spec: ScenarioSpec,
    ) -> None:
        super(AtariScenario, self).__init__(
            config,
            spec,
        )

        Log.out(
            "Initializing \"Atari\" fuser", {
            })
        self._fuser = AtariFuser(config)

        front_camera_dir = os.path.join(
            os.path.dirname(spec.path()),
            spec.data()['front_camera_dir'],
        )

        assert os.path.isdir(front_camera_dir)
        front_camera_paths = [
            f for f in os.listdir(front_camera_dir)
            if os.path.isfile(os.path.join(front_camera_dir, f))
        ]

        self._front_cameras = []
        for f in sorted(front_camera_paths):
            Log.out(
                "Loading front camera raw image", {
                    'filename': f,
                })
            self._front_cameras.append(
                cv2.imread(os.path.join(front_camera_dir, f)),
            )

    def run(
            self,
    ) -> bool:
        dump = {
            'bbox_detected': [],
            'lane_detected': [],
        }
        os.makedirs(self.dump_dir())

        for i, front_camera in enumerate(self._front_cameras):
            state, boxes, lanes = self._fuser.fuse(i/30, front_camera)

            dump['bbox_detected'].append([dict(b) for b in boxes])
            dump['lane_detected'].append([dict(l) for l in lanes])

            cv2.imwrite(
                os.path.join(self.dump_dir(), str(i) + ".png"),
                cv2.resize(
                    front_camera, (640, 360),
                    interpolation=cv2.INTER_LINEAR,
                ),
            )

        dump_path = os.path.join(self.dump_dir(), "dump.json")

        with open(dump_path, 'w') as out:
            json.dump(dump, out, indent=2)

    def view(
            self,
    ) -> str:
        return self._config.get('utils_viewer_url') + \
            'scenarios/perception.fusion.atari/' + self._id
