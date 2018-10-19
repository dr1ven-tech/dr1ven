import cv2
import numpy as np
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

    def color_filter(
            self,
            image,
    ):
        # image = cv2.resize(image, (0, 0), fx=0.5, fy=0.5)
        mask = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        mask_rl = cv2.inRange(
            mask, np.array([0, 100, 100]), np.array([10, 255, 255]),
        )
        mask_rh = cv2.inRange(
            mask, np.array([160, 100, 100]), np.array([179, 255, 255]),
        )
        mask_r = cv2.addWeighted(mask_rl, 1.0, mask_rh, 1.0, 0)
        mask_b = cv2.inRange(
            mask, np.array([100, 100, 100]), np.array([130, 255, 255]),
        )

        mask = cv2.addWeighted(mask_r, 1.0, mask_b, 1.0, 0.0)

        return cv2.bitwise_and(image, image, mask=mask)

    def extract_orb_matches(
            self,
    ):
        orb = cv2.ORB_create()
        kp1, des1 = orb.detectAndCompute(self._left, None)
        kp2, des2 = orb.detectAndCompute(self._right, None)

        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)

        matches = sorted(matches, key=lambda x: x.distance)

        dxs = [
            (kp1[m.queryIdx].pt[0] - kp2[m.trainIdx].pt[0]) for m in matches
        ]
        dxm = np.median(dxs)
        dys = [
            (kp1[m.queryIdx].pt[1] - kp2[m.trainIdx].pt[1]) for m in matches
        ]
        dym = np.median(dys)

        good = []
        pts1 = []
        pts2 = []
        for i, m in enumerate(matches):
            ddx = np.abs(dxs[i] - dxm) / np.abs(dxm)
            ddy = np.abs(dys[i] - dym) / np.abs(dym)
            if ddx < 0.2 and ddy < 0.2:
                good.append(m)
                pts2.append(kp2[m.trainIdx].pt)
                pts1.append(kp1[m.queryIdx].pt)
                # print("M {} {} {}".format(dxs[i], dys[i], dxs[i]/dys[i]))

        ptsl = np.int32(pts1)
        ptsr = np.int32(pts2)

        return good, ptsl, ptsr

    def run(
            self,
    ) -> bool:
        dump_path = os.path.join(self.dump_dir(), "dump.json")

        left = self._left
        right = self._right

        # left = self.color_filter(self._left)
        # right = self.color_filter(self._right)

        good, ptsl, ptsr = self.extract_orb_matches()

        for p in ptsl:
            left = cv2.rectangle(
                left,
                tuple(p-np.array([5, 5])), tuple(p+np.array([5, 5])),
                (0, 255, 0), 1,
            )
        for p in ptsr:
            right = cv2.rectangle(
                right,
                tuple(p-np.array([5, 5])), tuple(p+np.array([5, 5])),
                (0, 255, 0), 1,
            )

        F, mask = cv2.findFundamentalMat(ptsl, ptsr, cv2.FM_LMEDS)

        left_path = os.path.join(self.dump_dir(), "left.png")
        right_path = os.path.join(self.dump_dir(), "right.png")

        Log.out(
            "Dumping state", {
                'path': dump_path,
            })

        os.makedirs(self.dump_dir())

        cv2.imwrite(left_path, left)
        cv2.imwrite(right_path, right)

    def view(
            self,
    ) -> str:
        return self._config.get('utils_viewer_url') + \
            'scenarios/perception.stereo/' + self._id
