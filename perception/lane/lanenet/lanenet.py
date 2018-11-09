import cv2
import numpy as np
import os
import tensorflow as tf
import typing

from perception.lane.detector import Lane, LaneDetector

from perception.lane.lanenet.lanenet_tf.config import global_config
from perception.lane.lanenet.lanenet_tf.lanenet_model \
    import lanenet_merge_model, lanenet_cluster, lanenet_postprocess

from sensors.camera import CameraImage

from utils.config import Config

CFG = global_config.cfg
VGG_MEAN = [103.939, 116.779, 123.68]


class LaneNet(LaneDetector):
    def __init__(
            self,
            config: Config,
    ) -> None:
        super(LaneNet, self).__init__(config)

        self._net = lanenet_merge_model.LaneNet(
            phase=tf.constant('test', tf.string), net_flag='vgg'
        )

        self._input_tensor = tf.placeholder(
                dtype=tf.float32, shape=[1, 256, 512, 3], name='input_tensor',
            )
        self._binary_seg_ret, self._instance_seg_ret = self._net.inference(
            input_tensor=self._input_tensor,
            name='lanenet_model',
        )

        self._cluster = lanenet_cluster.LaneNetCluster()
        self._postprocessor = lanenet_postprocess.LaneNetPoseProcessor()

        self._saver = tf.train.Saver()

        if config.get("perception_device") == "cpu":
            sess_config = tf.ConfigProto(device_count={'CPU': 1})
        else:
            sess_config = tf.ConfigProto(device_count={'GPU': 1})

        sess_config.gpu_options.per_process_gpu_memory_fraction = \
            CFG.TEST.GPU_MEMORY_FRACTION
        sess_config.gpu_options.allow_growth = CFG.TRAIN.TF_ALLOW_GROWTH
        sess_config.gpu_options.allocator_type = 'BFC'

        self._sess = tf.Session(config=sess_config)

        weights_path = os.path.join(
            os.path.dirname(os.path.abspath(os.path.realpath(__file__))),
            "lanenet_tf", "weights",
            "tusimple_lanenet_vgg_2018-10-19-13-33-56.ckpt-200000",
        )

        with self._sess.as_default():
            self._saver.restore(
                sess=self._sess,
                save_path=weights_path,
            )

    def close(
            self,
    ):
        super(LaneNet, self).close()
        self._sess.close()

    def detect(
            self,
            image: CameraImage,
    ) -> typing.List[Lane]:
        assert self._closed is False
        assert image.data().shape[2] == 3
        assert image.data().shape[1] / image.data().shape[0] == 1280 / 720
        assert image.camera().bird_eye_input_size()[0] == 512
        assert image.camera().bird_eye_input_size()[1] == 256

        resized = image.data(size=(512, 256))
        resized = resized - VGG_MEAN

        with self._sess.as_default():
            binary_seg_image, instance_seg_image = self._sess.run(
                [self._binary_seg_ret, self._instance_seg_ret],
                feed_dict={self._input_tensor: [resized]},
            )

            binary_seg_image[0] = self._postprocessor.postprocess(
                binary_seg_image[0],
            )

            lane_embedding_feats, lane_coordinate = \
                self._cluster._get_lane_area(
                    binary_seg_ret=binary_seg_image[0],
                    instance_seg_ret=instance_seg_image[0],
                )
            num_clusters, labels, cluster_centers = \
                self._cluster._cluster(lane_embedding_feats, bandwidth=1.5)

            if num_clusters > 8:
                cluster_sample_nums = []
                for i in range(num_clusters):
                    cluster_sample_nums.append(len(np.where(labels == i)[0]))
                sort_idx = np.argsort(-np.array(cluster_sample_nums, np.int64))
                cluster_index = np.array(range(num_clusters))[sort_idx[0:8]]
            else:
                cluster_index = range(num_clusters)

        raw_projected = []
        bird_eye_points = []
        fitted_points = []
        max_height = 5 * 256
        maximal_height = 0
        maximal_index = 0

        for index, i in enumerate(cluster_index):
            idx = np.where(labels == i)
            points = np.flip(lane_coordinate[idx], axis=1)

            projected = np.squeeze(
                cv2.perspectiveTransform(
                    np.array([points], dtype="float32"),
                    image.camera().bird_eye_projection(),
                ),
                axis=0,
            )

            max_height = min(max_height, int(projected[-1][1]))
            if abs(projected[-1][1] - projected[0][-1]) > maximal_height:
                maximal_height = abs(projected[-1][1] - projected[0][-1])
                maximal_index = i

            for j in range(projected.shape[0]):
                bird_eye_points.append(projected[j])

            x = np.float64(projected)[:, 0]
            y = np.float64(projected)[:, 1]

            Y = np.ones((y.size, 3))
            Y[:, 0] = y*y
            Y[:, 1] = y
            # Y = np.ones((y.size, 2))
            # Y[:, 0] = y

            w = np.dot(
                np.linalg.inv(np.dot(np.transpose(Y), Y)),
                np.dot(np.transpose(Y), x),
            )

            print("W: {}".format(w))

            coordinates = []
            for y in range(10*256):
                y = float(y)
                v = np.float64([y*y, y, 1])
                # v = np.float64([y, 1])
                x = np.dot(w, v)

                # rx = int(round(x * image.data().shape[1] / 512))
                # ry = int(round(y * image.data().shape[0] / 256))

                coordinates.append([x, y])
                fitted_points.append([x, y])

            raw_projected.append(coordinates)

        idx = np.where(labels == maximal_index)
        points = np.flip(lane_coordinate[idx], axis=1)

        projected = np.squeeze(
            cv2.perspectiveTransform(
                np.array([points], dtype="float32"),
                image.camera().bird_eye_projection(),
            ),
            axis=0,
        )

        projected = projected - np.array([
            raw_projected[maximal_index][max_height][0] - 256,
            0,
        ])

        road_fitted = []

        x = np.float64(projected)[:, 0]
        y = np.float64(projected)[:, 1]

        Y = np.ones((y.size, 3))
        Y[:, 0] = y*y
        Y[:, 1] = y

        w = np.dot(
            np.linalg.inv(np.dot(np.transpose(Y), Y)),
            np.dot(np.transpose(Y), x),
        )

        for y in range(5*256):
            y = float(y)
            v = np.float64([y*y, y, 1])
            x = np.dot(w, v)

            # rx = int(round(x * image.data().shape[1] / 512))
            # ry = int(round(y * image.data().shape[0] / 256))

            road_fitted.append(np.array([x, y]))

        for index, i in enumerate(cluster_index):
            coordinates = []
            for y in range(5*256):
                y = float(y)
                v = np.float64([y*y, y, 1])
                x = np.dot(w, v)

                coordinates.append(np.array([
                    x + raw_projected[i][max_height][0] - 256,
                    y,
                ]))

        raw_projected = cv2.perspectiveTransform(
            np.array(raw_projected, dtype="float32"),
            np.linalg.inv(image.camera().bird_eye_projection()),
        ).tolist()

        for l in raw_projected:
            for p in l:
                p[0] *= image.data().shape[1] / 512
                p[1] *= image.data().shape[0] / 256

        # filtered: typing.List[typing.List[typing.List[int]]] = \
        #     [[] for _ in raw_projected]
        # sign = None
        # for p in reversed(range(len(raw[0]))):
        #     for l in range(len(raw)):
        #         filtered[l].append(raw[l][p])
        #     cur = np.sign([raw[0][p][0] - l[p][0] for l in raw])
        #     if sign is None:
        #         sign = cur
        #     if not np.array_equal(sign, cur):
        #         break

        return [Lane(l) for l in raw_projected if len(l) > 2], bird_eye_points, fitted_points
