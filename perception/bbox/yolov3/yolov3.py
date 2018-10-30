import os
import perception.bbox.yolov3.darknet.python.darknet as darknet
import typing

from perception.bbox.detector import BBox, BBoxDetector

from utils.config import Config

from sensors.camera import CameraImage

from state.entity import EntityType


class YOLOv3(BBoxDetector):
    def __init__(
            self,
            config: Config,
    ) -> None:
        super(YOLOv3, self).__init__(config)

        darknet_dir = os.path.join(
            os.path.dirname(os.path.abspath(os.path.realpath(__file__))),
            "darknet",
        )

        self._net = darknet.load_net(
            bytes(
                os.path.join(darknet_dir, "cfg", "yolov3.cfg"),
                encoding='utf-8',
            ),
            bytes(
                os.path.join(darknet_dir, "yolov3.weights"),
                encoding='utf-8',
            ),
            0,
        )
        self._meta = darknet.load_meta_chdir(
            bytes(
                os.path.join(darknet_dir, "cfg", "coco.data"),
                encoding='utf-8',
            ),
        )

    def detect(
            self,
            image: CameraImage,
            size: typing.Optional[typing.Tuple[int, int]] = None,
    ) -> typing.List[BBox]:
        assert self._closed is False
        assert image.data().shape[2] == 3

        r = darknet.detect(self._net, self._meta, image.data(size=size))

        classes = {
            'car': EntityType.CAR,
            'truck': EntityType.TRUCK,
            'motorbike': EntityType.MOTORBIKE,
            'bus': EntityType.BUS,
            'person': EntityType.PERSON,
            'bird': EntityType.ANIMAL,
            'cat': EntityType.ANIMAL,
            'dog': EntityType.ANIMAL,
            'horse': EntityType.ANIMAL,
            'sheep': EntityType.ANIMAL,
            'cow': EntityType.ANIMAL,
        }

        boxes = []

        for p in r:
            if p[0].decode('utf-8') in classes:
                boxes.append(
                    BBox(
                        classes[p[0].decode('utf-8')],
                        p[1],
                        [int(p[2][0]-p[2][2]/2), int(p[2][1]-p[2][3]/2)],
                        [int(p[2][2]), int(p[2][3])],
                    )
                )

        return boxes


# def main():
#     image = cv2.imread(
#         "/home/spolu/scenarios/perception.bbox.detector/20181012_A6.png",
#     )
#     assert image is not None
#
#     yolov3 = YOLOv3(None)
#
#     boxes = yolov3.detect(image)
#
#     for b in boxes:
#         print("{}".format(dict(b)))
#
#     import pdb
#     pdb.set_trace()
