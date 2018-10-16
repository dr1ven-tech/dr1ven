import os
import perception.bbox.yolov3.darknet.python.darknet as darknet
import typing

from perception.bbox.detector import BBox, BBoxDetector

from utils.config import Config

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
            image,
    ) -> typing.List[BBox]:
        assert image.shape[2] == 3

        r = darknet.detect(self._net, self._meta, image)

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
                        [int(p[2][0]), int(p[2][1])],
                        [int(p[2][2]), int(p[2][3])],
                    )
                )

        return boxes


# def main():
#     yolov3 = YOLOv3(None)
#
#     darknet_dir = os.path.join(
#         os.path.dirname(os.path.abspath(os.path.realpath(__file__))),
#         "darknet",
#     )
#
#     image = cv2.imread(os.path.join(darknet_dir, "data", "dog.jpg"))
#     boxes = yolov3.detect(image)
#
#     print("{}".format(boxes))
#
#     import pdb
#     pdb.set_trace()
