import typing

import torch.nn as nn

from utils.config import Config


class ResidualBlock(nn.Module):
    """ `ResidualBlock` implements a residual block.

    Input dimension `dim`. Outputs `dim` filters.
    """
    def __init__(
            self,
            config: Config,
            dim: int,
    ) -> None:
        super(ResidualBlock, self).__init__()

        layers = [
            nn.Conv2d(
                dim, dim//2,
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


class YOLOv3(nn.Module):
    def __init__(
            self,
            config: Config,
    ) -> None:
        super(YOLOv3, self).__init__()

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
                    nn.Conv2d(
                        1024, 512,
                        kernel_size=1, stride=1, padding=0, bias=False
                    ),
                    nn.BatchNorm2d(512),
                    nn.LeakyReLU(0.1, True),
                    nn.ReflectionPad2d(1),
                    nn.Conv2d(
                        512, 1024,
                        kernel_size=3, stride=1, padding=0, bias=False
                    ),
                    nn.BatchNorm2d(1024),
                    nn.LeakyReLU(0.1, True),

                    nn.Conv2d(
                        1024, 512,
                        kernel_size=1, stride=1, padding=0, bias=False
                    ),
                    nn.BatchNorm2d(512),
                    nn.LeakyReLU(0.1, True),
                    nn.ReflectionPad2d(1),
                    nn.Conv2d(
                        512, 1024,
                        kernel_size=3, stride=1, padding=0, bias=False
                    ),
                    nn.BatchNorm2d(1024),
                    nn.LeakyReLU(0.1, True),

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
                        1024, 255,
                        kernel_size=1, stride=1, padding=0, bias=True
                    ),
                ]
            ],
            # YOLO 2
            [
                [
                    UpsampleBlock(config, 512),
                ],
                [
                    nn.Conv2d(
                        256+512, 256,
                        kernel_size=1, stride=1, padding=0, bias=False
                    ),
                    nn.BatchNorm2d(256),
                    nn.LeakyReLU(0.1, True),
                    nn.ReflectionPad2d(1),
                    nn.Conv2d(
                        256, 512,
                        kernel_size=3, stride=1, padding=0, bias=False
                    ),
                    nn.BatchNorm2d(512),
                    nn.LeakyReLU(0.1, True),

                    nn.Conv2d(
                        512, 256,
                        kernel_size=1, stride=1, padding=0, bias=False
                    ),
                    nn.BatchNorm2d(256),
                    nn.LeakyReLU(0.1, True),
                    nn.ReflectionPad2d(1),
                    nn.Conv2d(
                        256, 512,
                        kernel_size=3, stride=1, padding=0, bias=False
                    ),
                    nn.BatchNorm2d(512),
                    nn.LeakyReLU(0.1, True),

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
                        512, 255,
                        kernel_size=1, stride=1, padding=0, bias=True
                    ),
                ]
            ]
            # YOLO 3
            [
                [
                    UpsampleBlock(config, 256),
                ],
                [
                    nn.Conv2d(
                        128+256, 128,
                        kernel_size=1, stride=1, padding=0, bias=False
                    ),
                    nn.BatchNorm2d(128),
                    nn.LeakyReLU(0.1, True),
                    nn.ReflectionPad2d(1),
                    nn.Conv2d(
                        128, 256,
                        kernel_size=3, stride=1, padding=0, bias=False
                    ),
                    nn.BatchNorm2d(256),
                    nn.LeakyReLU(0.1, True),

                    nn.Conv2d(
                        256, 128,
                        kernel_size=1, stride=1, padding=0, bias=False
                    ),
                    nn.BatchNorm2d(128),
                    nn.LeakyReLU(0.1, True),
                    nn.ReflectionPad2d(1),
                    nn.Conv2d(
                        128, 256,
                        kernel_size=3, stride=1, padding=0, bias=False
                    ),
                    nn.BatchNorm2d(256),
                    nn.LeakyReLU(0.1, True),

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
                        256, 255,
                        kernel_size=1, stride=1, padding=0, bias=True
                    ),
                ]
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
        x0 = self.shared[0](x)
        x1 = self.shared[1](x0)
        x2 = self.shared[2](x1)

        y0 = self.yolo0(x2)

        return y0
