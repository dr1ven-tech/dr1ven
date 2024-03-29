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

        self._f = spec.data()['camera']['f']
        self._c_x = spec.data()['camera']['c_x']
        self._c_y = spec.data()['camera']['c_y']

        self._A = np.array([
            [self._f, 0, self._c_x],
            [0, self._f, self._c_y],
            [0, 0, 1],
        ])

    def detect_straight_lines(
            self,
            image,
    ):
        mask = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)
        mask = cv2.inRange(
            mask, np.array([0, 130, 0]), np.array([255, 255, 255]),
        )

        mask[0:int(mask.shape[0]/2), :] = 0

        image = cv2.bitwise_and(image, image, mask=mask)
        filtered = cv2.GaussianBlur(image, (25, 25), 0)

        edges = cv2.Canny(
            filtered.astype(np.uint8), 100, 150, apertureSize=3,
        )

        # lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 80, 30, 10)

        # for l in lines:
        #     x1, y1, x2, y2 = l[0]
        #     cv2.line(image, (x1, y1), (x2, y2), (0, 0, 255), 5)

        lines = cv2.HoughLines(
            edges, 1, np.pi / 180, 120,
        )

        processed_lines = []

        for l in lines:
            rho, theta = l[0]
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a*rho
            y0 = b*rho
            pt1 = (int(x0 + 5000*(-b)), int(y0 + 5000*(a)))
            pt2 = (int(x0 - 5000*(-b)), int(y0 - 5000*(a)))

            _, pt1, pt2 = cv2.clipLine(
                (0, 0, image.shape[1], image.shape[0]),
                pt1, pt2,
            )

            if pt1[1] > image.shape[0]/4 and pt2[1] > image.shape[0]/4:
                continue
            if abs(pt2[0]-pt2[1]) < 10:
                continue

            processed_lines.append(
                [pt1, pt2, (pt2[1] - pt1[1])/(pt2[0] - pt1[0])]
            )

        selected_lines = []
        for l in processed_lines:
            skip = False
            for s in selected_lines:
                if abs(s[2] - l[2]) < 1/3:
                    skip = True
            if skip:
                continue

            selected_lines.append(l)

        final_lines = list(reversed(
                sorted(selected_lines, key=lambda l: abs(l[2]))
        ))[0:2]

        return final_lines, filtered

    def red_blue_color_filter(
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
            left,
            right,
    ):
        orb = cv2.ORB_create()
        kp1, des1 = orb.detectAndCompute(
            cv2.cvtColor(left, cv2.COLOR_BGR2GRAY),
            None,
        )
        kp2, des2 = orb.detectAndCompute(
            cv2.cvtColor(right, cv2.COLOR_BGR2GRAY),
            None,
        )

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

        pts1 = np.int32(pts1)
        pts2 = np.int32(pts2)

        return good, pts1, pts2

    def extract_sift_matches(
            self,
            left,
            right,
    ):
        sift = cv2.xfeatures2d.SIFT_create()

        kp1, des1 = sift.detectAndCompute(
            cv2.cvtColor(left, cv2.COLOR_BGR2GRAY),
            None,
        )
        kp2, des2 = sift.detectAndCompute(
            cv2.cvtColor(right, cv2.COLOR_BGR2GRAY),
            None,
        )

        bf = cv2.BFMatcher(cv2.NORM_L2)
        matches = bf.knnMatch(des1, des2, k=2)

        dxs = [
            (kp1[m.queryIdx].pt[0] - kp2[m.trainIdx].pt[0]) for m, _ in matches
        ]
        dxm = np.median(dxs)
        dys = [
            (kp1[m.queryIdx].pt[1] - kp2[m.trainIdx].pt[1]) for m, _ in matches
        ]
        dym = np.median(dys)

        good = []
        pts1 = []
        pts2 = []
        for i, (m, n) in enumerate(matches):
            ddx = np.abs(dxs[i] - dxm) / np.abs(dxm)
            ddy = np.abs(dys[i] - dym) / np.abs(dym)
            if m.distance < 0.75*n.distance and ddx < 0.2 and ddy < 0.2:
                good.append(m)
                pts2.append(kp2[m.trainIdx].pt)
                pts1.append(kp1[m.queryIdx].pt)

        # match = cv2.drawMatchesKnn(
        #     left, kp1,
        #     right, kp2,
        #     good,
        #     None,
        #     flags=2,
        # )

        pts1 = np.int32(pts1)
        pts2 = np.int32(pts2)

        return good, pts1, pts2

    def stereo_rectify(
            self,
            left,
            right,
            pts1,
            pts2,
    ):
        E, mask = cv2.findEssentialMat(
            pts1, pts2, self._A, method=cv2.RANSAC,
        )

        fpts1 = pts1[mask.ravel() == 1]
        fpts2 = pts2[mask.ravel() == 1]

        _, r, t, mask = cv2.recoverPose(E, fpts1, fpts2, self._A)
        # r1, r2, t = cv2.decomposeEssentialMat(E)

        R1, R2, P1, P2, Q, _, _ = cv2.stereoRectify(
            self._A, np.zeros(4),
            self._A, np.zeros(4),
            (left.shape[1], left.shape[0]),
            r, t,
            # newImageSize=(left.shape[1], left.shape[0]),
            flags=cv2.CALIB_ZERO_DISPARITY,
        )

        # import pdb; pdb.set_trace()

        map1x, map1y = cv2.initUndistortRectifyMap(
            self._A, np.zeros(4),
            R1, P1,
            (left.shape[1], left.shape[0]),
            cv2.CV_32FC1,
        )
        map2x, map2y = cv2.initUndistortRectifyMap(
            self._A, np.zeros(4),
            R2, P2,
            (left.shape[1], left.shape[0]),
            cv2.CV_32FC1,
        )

        # import pdb; pdb.set_trace()

        left = cv2.remap(left, map1x, map1y, cv2.INTER_LINEAR)
        right = cv2.remap(right, map2x, map2y, cv2.INTER_LINEAR)

        rpts1 = cv2.undistortPoints(
            np.float64(np.expand_dims(fpts1, 1)),
            self._A, np.zeros(4), R=R1, P=P1,
        ).squeeze(1)
        rpts2 = cv2.undistortPoints(
            np.float64(np.expand_dims(fpts2, 1)),
            self._A, np.zeros(4), R=R2, P=P2,
        ).squeeze(1)

        return left, right, fpts1, fpts2, rpts1, rpts2, Q

    def run(
            self,
    ) -> bool:
        dump_path = os.path.join(self.dump_dir(), "dump.json")

        left = self._left
        right = self._right

        # good, pts1, pts2 = self.extract_orb_matches(left, right)
        good, pts1, pts2 = self.extract_sift_matches(left, right)

        left, right, fpts1, fpts2, rpts1, rpts2, Q = self.stereo_rectify(
            left, right, pts1, pts2,
        )

        for p in rpts1:
            left = cv2.rectangle(
                left,
                tuple(np.int64(p-np.array([5, 5]))),
                tuple(np.int64(p+np.array([5, 5]))),
                (0, 255, 0), 1,
            )
        for p in rpts2:
            right = cv2.rectangle(
                right,
                tuple(np.int64(p-np.array([5, 5]))),
                tuple(np.int64(p+np.array([5, 5]))),
                (0, 255, 0), 1,
            )

        for i in range(len(rpts1)):
            z = self._f / abs(rpts1[i][0] - rpts2[i][0])
            left = cv2.putText(
                left, "{}".format(z),
                (int(rpts1[i][0]), int(rpts1[i][1])), 1, 1, (255, 0, 0), 2, 0,
            )

        # left_lines, _ = self.detect_straight_lines(left)
        # right_lines, _ = self.detect_straight_lines(right)

        # for l in left_lines:
        #     if l[2] >= 0:
        #         cv2.line(left, l[0], l[1], (0, 0, 255), 2)
        #     else:
        #         cv2.line(left, l[0], l[1], (255, 0, 0), 2)

        # for l in right_lines:
        #     if l[2] >= 0:
        #         cv2.line(right, l[0], l[1], (0, 0, 255), 2)
        #     else:
        #         cv2.line(right, l[0], l[1], (255, 0, 0), 2)

        # T = np.float32([[1, 0, 360], [0, 1, 0]])
        # left = cv2.warpAffine(left, T, (3840, 2160))

        # left = cv2.warpPerspective(left, h1, (3840, 2160))
        # right = cv2.warpPerspective(right, h2, (3840, 2160))

        # window_size = 5
        # left_matcher = cv2.StereoSGBM_create(
        #         minDisparity=0,
        #         numDisparities=160,
        #         blockSize=5,
        #         P1=8 * 3 * window_size ** 2,
        #         P2=32 * 3 * window_size ** 2,
        #         disp12MaxDiff=1,
        #         uniquenessRatio=15,
        #         speckleWindowSize=0,
        #         speckleRange=2,
        #         preFilterCap=63,
        #         mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY
        # )

        # right_matcher = cv2.ximgproc.createRightMatcher(left_matcher)

        # lmbda = 80000
        # sigma = 1.2
        # wls_filter = cv2.ximgproc.createDisparityWLSFilter(
        #     matcher_left=left_matcher
        # )
        # wls_filter.setLambda(lmbda)
        # wls_filter.setSigmaColor(sigma)

        # disparity = left_matcher.compute(
        #     cv2.cvtColor(left, cv2.COLOR_BGR2GRAY),
        #     cv2.cvtColor(right, cv2.COLOR_BGR2GRAY),
        # )
        # dispr = right_matcher.compute(right, left)  # .astype(np.float32)/16
        # displ = np.int16(displ)
        # dispr = np.int16(dispr)
        # disparity = wls_filter.filter(displ, left, None, dispr)

        # stereo = cv2.StereoBM_create(blockSize=11)
        # disparity = stereo.compute(
        #     cv2.cvtColor(left, cv2.COLOR_BGR2GRAY),
        #     cv2.cvtColor(right, cv2.COLOR_BGR2GRAY),
        # ).astype(np.float)

        # import pdb
        # pdb.set_trace()
        # depth = cv2.reprojectImageTo3D(disparity, Q)

        # disparity = disparity.astype(np.float)
        # disparity = cv2.normalize(
        #     src=disparity, dst=disparity,
        #     beta=0, alpha=255, norm_type=cv2.NORM_MINMAX,
        # )
        # import pdb
        # pdb.set_trace()
        # disparity -= disparity.min()
        # disparity = disparity * (255 / disparity.max())

        left_path = os.path.join(self.dump_dir(), "left.png")
        right_path = os.path.join(self.dump_dir(), "right.png")
        # disparity_path = os.path.join(self.dump_dir(), "disparity.png")

        Log.out(
            "Dumping state", {
                'path': dump_path,
            })

        os.makedirs(self.dump_dir())

        cv2.imwrite(left_path, left)
        cv2.imwrite(right_path, right)
        # cv2.imwrite(disparity_path, disparity)

    def view(
            self,
    ) -> str:
        return self._config.get('utils_viewer_url') + \
            'scenarios/perception.stereo/' + self._id
