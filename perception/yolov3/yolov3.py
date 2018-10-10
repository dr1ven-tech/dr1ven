import torch
import torch.nn as nn
import typing

from utils.config import Config


class Block(nn.Module):
    """ `ResidualBlock` implements a residual block.

    Input dimension `dim`. Outputs `dim` filters.
    """
    def __init__(
            self,
            config: Config,
            dim: int,
            extra: int = 0,
    ) -> None:
        super(Block, self).__init__()

        layers = [
            nn.Conv2d(
                dim+extra, dim//2,
                kernel_size=1, stride=1, padding=0, bias=False
            ),
            nn.BatchNorm2d(dim//2),
            nn.LeakyReLU(0.1, True),
        ]

        layers += [
            nn.ReflectionPad2d(1),
            nn.Conv2d(
                dim//2, dim,
                kernel_size=3, stride=1, padding=0, bias=False
            ),
            nn.BatchNorm2d(dim),
            nn.LeakyReLU(0.1, True),
        ]

        self.layers = nn.Sequential(*layers)

    def forward(
            self,
            x,
    ):
        return x


class ResidualBlock(Block):
    """ `ResidualBlock` implements a residual block.

    Input dimension `dim`. Outputs `dim` filters.
    """
    def __init__(
            self,
            config: Config,
            dim: int,
    ) -> None:
        super(ResidualBlock, self).__init__(config, dim)

    def forward(
            self,
            x,
    ):
        return (x + self.layers(x))


class DownsampleBlock(nn.Module):
    """ `DownsampleBlock` implements a downsample block.

    Input dimension `dim`. Outputs `2*dim` filters.
    """

    def __init__(
            self,
            config: Config,
            dim: int,
    ) -> None:
        super(DownsampleBlock, self).__init__()

        layers = [
            nn.ReflectionPad2d(1),
            nn.Conv2d(
                dim, 2*dim,
                kernel_size=3, stride=2, padding=0, bias=False
            ),
            nn.BatchNorm2d(2*dim),
            nn.LeakyReLU(0.1, True),
        ]

        self.layers = nn.Sequential(*layers)

    def forward(
            self,
            x,
    ):
        return self.layers(x)


class UpsampleBlock(nn.Module):
    """ `UpsampleBlock` implements an upsample block.

    Input dimension `dim`. Outputs `dim/2` filters.
    """

    def __init__(
            self,
            config: Config,
            dim: int,
    ) -> None:
        super(UpsampleBlock, self).__init__()

        layers = [
            nn.Conv2d(
                dim, dim//2,
                kernel_size=1, stride=1, padding=0, bias=False
            ),
            nn.BatchNorm2d(dim),
            nn.LeakyReLU(0.1, True),

            nn.Upsample(
                scale_factor=2, mode="nearest",
            )
        ]

        self.layers = nn.Sequential(*layers)

    def forward(
            self,
            x,
    ):
        return self.layers(x)


class DetectionLayer(nn.Module):
    """ `DetectionLayer` implements the final detection logic.
    """

    def __init__(
            self,
            config: Config,
            anchors: typing.List[typing.List[int]],
    ) -> None:
        super(DetectionLayer, self).__init__()

        self.ignore_threshold = config.get(
            "perception_yolov3_ingore_threshold",
        )
        self.image_size = config.get(
            "perception_yolov3_image_size",
        )
        self.classes_count = config.get(
            "perception_yolov3_classes_count",
        )
        self.device = torch.device(config.get('perception_device'))

        assert len(anchors) == 3

        self.anchors = anchors

    def forward(
            self,
            x,
    ):
        nB = x.size(0)
        nG = x.size(2)

        stride = self.image_size / nG

        prediction = x.view(
            nB,
            3,
            5 + self.classes_count,
            nG, nG,
        ).permute(0, 1, 3, 4, 2).contiguous()

        x = torch.sigmoid(prediction[..., 0])  # Center x
        y = torch.sigmoid(prediction[..., 1])  # Center y
        w = prediction[..., 2]  # Width
        h = prediction[..., 3]  # Height

        pred_objectness = torch.sigmoid(prediction[..., 4])  # Objectness
        pred_class = torch.sigmoid(prediction[..., 5:])      # Class

        grid_x = torch.arange(nG).repeat(
            nG, 1
        ).view([1, 1, nG, nG]) .float().to(self.device)
        grid_y = torch.arange(nG).repeat(
            nG, 1
        ).t().view([1, 1, nG, nG]).float().to(self.device)

        scaled_anchors = torch.FloatTensor(
            [(a_w / stride, a_h / stride) for a_w, a_h in self.anchors]
        ).to(self.device)

        anchor_w = scaled_anchors[:, 0:1].view((1, 3, 1, 1))
        anchor_h = scaled_anchors[:, 1:2].view((1, 3, 1, 1))

        pred_boxes = torch.FloatTensor(
            prediction[..., :4].shape
        ).to(self.device)

        pred_boxes[..., 0] = x.data + grid_x
        pred_boxes[..., 1] = y.data + grid_y
        pred_boxes[..., 2] = torch.exp(w.data) * anchor_w
        pred_boxes[..., 3] = torch.exp(h.data) * anchor_h

        return torch.cat(
            (
                pred_boxes.view(nB, -1, 4) * stride,
                pred_objectness.view(nB, -1, 1),
                pred_class.view(nB, -1, self.classes_count),
            ),
            -1,
        )


class YOLOv3(nn.Module):
    def __init__(
            self,
            config: Config,
    ) -> None:
        super(YOLOv3, self).__init__()

        self.classes_count = config.get(
            "perception_yolov3_classes_count",
        )

        shared = [
            [
                nn.ReflectionPad2d(1),
                nn.Conv2d(
                    3, 32,
                    kernel_size=3, stride=1, padding=0, bias=False
                ),
                nn.BatchNorm2d(32),
                nn.LeakyReLU(0.1, True),

                DownsampleBlock(config, 32),
                ResidualBlock(config, 64),

                DownsampleBlock(config, 64),
                ResidualBlock(config, 128),
                ResidualBlock(config, 128),

                DownsampleBlock(config, 128),
                ResidualBlock(config, 256),
                ResidualBlock(config, 256),
                ResidualBlock(config, 256),
                ResidualBlock(config, 256),
                ResidualBlock(config, 256),
                ResidualBlock(config, 256),
                ResidualBlock(config, 256),
                ResidualBlock(config, 256),  # layers 36
            ],
            [
                DownsampleBlock(config, 256),
                ResidualBlock(config, 512),
                ResidualBlock(config, 512),
                ResidualBlock(config, 512),
                ResidualBlock(config, 512),
                ResidualBlock(config, 512),
                ResidualBlock(config, 512),
                ResidualBlock(config, 512),
                ResidualBlock(config, 512),  # layers 61
            ],
            [
                DownsampleBlock(config, 512),
                ResidualBlock(config, 1024),
                ResidualBlock(config, 1024),
                ResidualBlock(config, 1024),
                ResidualBlock(config, 1024),  # layers 74
            ]
        ]

        yolo = [
            # YOLO 1
            [
                [],
                [
                    Block(config, 1024),
                    Block(config, 1024),

                    nn.Conv2d(
                        1024, 512,
                        kernel_size=1, stride=1, padding=0, bias=False
                    ),
                    nn.BatchNorm2d(512),
                    nn.LeakyReLU(0.1, True),
                ],
                [
                    nn.ReflectionPad2d(1),
                    nn.Conv2d(
                        512, 1024,
                        kernel_size=3, stride=1, padding=0, bias=False
                    ),
                    nn.BatchNorm2d(1024),
                    nn.LeakyReLU(0.1, True),

                    nn.Conv2d(
                        1024, 3 * self.classes_count,
                        kernel_size=1, stride=1, padding=0, bias=True
                    ),
                ],
                [
                    DetectionLayer(
                        config,
                        [[116, 90], [156, 198], [373, 326]],
                    )
                ],
            ],
            # YOLO 2
            [
                [
                    UpsampleBlock(config, 512),
                ],
                [
                    Block(config, 512, 216),
                    Block(config, 512),

                    nn.Conv2d(
                        512, 256,
                        kernel_size=1, stride=1, padding=0, bias=False
                    ),
                    nn.BatchNorm2d(256),
                    nn.LeakyReLU(0.1, True),
                ],
                [
                    nn.ReflectionPad2d(1),
                    nn.Conv2d(
                        256, 512,
                        kernel_size=3, stride=1, padding=0, bias=False
                    ),
                    nn.BatchNorm2d(512),
                    nn.LeakyReLU(0.1, True),

                    nn.Conv2d(
                        512, 3 * self.classes_count,
                        kernel_size=1, stride=1, padding=0, bias=True
                    ),
                ],
                [
                    DetectionLayer(
                        config,
                        [[30, 61], [62, 45], [59, 119]],
                    )
                ],
            ]
            # YOLO 3
            [
                [
                    UpsampleBlock(config, 256),
                ],
                [
                    Block(config, 256, 128),
                    Block(config, 256),

                    nn.Conv2d(
                        256, 128,
                        kernel_size=1, stride=1, padding=0, bias=False
                    ),
                    nn.BatchNorm2d(128),
                    nn.LeakyReLU(0.1, True),
                ],
                [
                    nn.ReflectionPad2d(1),
                    nn.Conv2d(
                        128, 256,
                        kernel_size=3, stride=1, padding=0, bias=False
                    ),
                    nn.BatchNorm2d(256),
                    nn.LeakyReLU(0.1, True),

                    nn.Conv2d(
                        256, 3 * self.classes_count,
                        kernel_size=1, stride=1, padding=0, bias=True
                    ),
                ],
                [
                    DetectionLayer(
                        config,
                        [[10, 13], [16, 30], [33, 23]],
                    )
                ],
            ]
        ]

        self.shared = [nn.Sequential(*l) for l in shared]
        self.yolo = [
            [nn.Sequential(*l) for l in block] for block in yolo
        ]

    def forward(
            self,
            x,
    ):
        l36 = self.shared[0](x)
        l61 = self.shared[1](l36)
        l74 = self.shared[2](l61)

        y0_1 = self.yolo[0][1](l74)
        y0_2 = self.yolo[0][2](y0_1)
        y0_3 = self.yolo[0][3](y0_2)

        y1_0 = self.yolo[1][0](y0_2)
        y1_1 = self.yolo[1][1](torch.cat((y1_0, l61)))
        y1_2 = self.yolo[1][2](y1_1)
        y1_3 = self.yolo[1][2](y1_2)

        y2_0 = self.yolo[2][0](y1_2)
        y2_1 = self.yolo[2][1](torch.cat((y2_0, l36)))
        y2_2 = self.yolo[2][2](y2_1)
        y2_3 = self.yolo[2][2](y2_2)

        return torch.cat((y0_3, y1_3, y2_3), 1)
