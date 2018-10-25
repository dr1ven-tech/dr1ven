import cv2
import os
import tensorflow as tf
import typing

from perception.lane.detector import Lane, LaneDetector

from perception.lane.lanenet.lanenet_tf.config import global_config
from perception.lane.lanenet.lanenet_tf.lanenet_model \
    import lanenet_merge_model, lanenet_cluster, lanenet_postprocess

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

        # if config.get("perception_device") == "cpu":
        sess_config = tf.ConfigProto(device_count={'GPU': 1})
        # else:
        #     sess_config = tf.ConfigProto(device_count={'GPU': 1})

        sess_config.gpu_options.per_process_gpu_memory_fraction = \
            CFG.TEST.GPU_MEMORY_FRACTION
        sess_config.gpu_options.allow_growth = CFG.TRAIN.TF_ALLOW_GROWTH
        sess_config.gpu_options.allocator_type = 'BFC'

        self._sess = tf.Session(config=sess_config)

        weights_path = os.path.join(
            os.path.dirname(os.path.abspath(os.path.realpath(__file__))),
            "lanenet_tf", "weights", "tusimple_lanenet_vgg_2018-10-19-13-33-56.ckpt-200000",
        )

        with self._sess.as_default():
            self._saver.restore(
                sess=self._sess,
                save_path=weights_path,
            )

    def __enter__(
            self,
    ):
        return self

    def __exit__(
            self,
            exc_type,
            exc_val,
            exc_tb,
    ):
        self.close()

    def close(
            self,
    ):
        self._session.close()

    def detect(
            self,
            image,
    ) -> typing.List[Lane]:
        assert image.shape[2] == 3
        assert image.shape[1] / image.shape[0] == 1280 / 720

        image = cv2.resize(image, (512, 256), interpolation=cv2.INTER_LINEAR)
        image = image - VGG_MEAN

        with self._sess.as_default():
            binary_seg_image, instance_seg_image = self._sess.run(
                [self._binary_seg_ret, self._instance_seg_ret],
                feed_dict={self._input_tensor: [image]},
            )

            binary_seg_image[0] = self._postprocessor.postprocess(
                binary_seg_image[0],
            )
            mask_image = self._cluster.get_lane_mask(
                binary_seg_ret=binary_seg_image[0],
                instance_seg_ret=instance_seg_image[0],
            )

            # for i in range(4):
            #     instance_seg_image[0][:, :, i] = minmax_scale(
            #         instance_seg_image[0][:, :, i]
            #     )
            # embedding_image = np.array(instance_seg_image[0], np.uint8)

            # plt.figure('mask_image')
            # plt.imshow(mask_image[:, :, (2, 1, 0)])
            # plt.figure('instance_image')
            # plt.imshow(embedding_image[:, :, (2, 1, 0)])
            # plt.figure('binary_image')
            # plt.imshow(binary_seg_image[0] * 255, cmap='gray')
            # plt.show()

        return mask_image
