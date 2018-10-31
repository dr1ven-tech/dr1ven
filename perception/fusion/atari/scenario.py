import cv2
import json
import os

from perception.fusion.atari.atari import Atari

from sensors.camera import Camera, CameraImage

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
            "Initializing fusion", {
                'version': "atari",
            })
        self._atari = Atari(config, spec.data()['lane_count'])

        camera = Camera.from_dict(spec.data()['camera'])

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
                "Loading front camera image", {
                    'filename': f,
                })
            self._front_cameras.append(
                CameraImage.from_path_and_camera(
                    os.path.join(front_camera_dir, f),
                    camera,
                )
            )

    def run(
            self,
    ) -> bool:
        dump = {
            'bbox_detected': [],
            'lane_detected': [],
            'steps': [],
        }
        os.makedirs(self.dump_dir())

        for i, front_camera in enumerate(self._front_cameras):
            state, boxes, lanes = self._atari.fuse(i/30, front_camera)

            dump['bbox_detected'].append([dict(b) for b in boxes])
            dump['lane_detected'].append([dict(l) for l in lanes])
            dump['steps'].append({
                'step': i,
                'state': dict(state),
            })

            cv2.imwrite(
                os.path.join(self.dump_dir(), str(i) + ".png"),
                front_camera.data(size=(640, 360)),
            )

        dump_path = os.path.join(self.dump_dir(), "dump.json")

        with open(dump_path, 'w') as out:
            json.dump(dump, out, indent=2)

    def view(
            self,
    ) -> str:
        return self._config.get('utils_viewer_url') + \
            'scenarios/perception.fusion.atari/' + self._id
