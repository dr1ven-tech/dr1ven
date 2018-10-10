import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F

class ResidualBlock(nn.Module):
    """ `ResidualBlock` implements a residual block.

    Input dimension `dim`. Outputs `dim` filters.
    """

    def __init__(self, config, dim):
        super(ResidualBlock, self).__init__()

        layers = [
            nn.Conv2d(
                dim, dim//2, kernel_size=1, stride=1, padding=0, bias=False
            ),
            nn.BatchNorm2d(dim//2),
            nn.LeakyReLU(0.1, True),
        ]

        layers += [
            nn.ReflectionPad2d(1),
            nn.Conv2d(
                dim//2, dim, kernel_size=3, stride=1, padding=0, bias=False
            ),
            nn.BatchNorm2d(dim),
            nn.LeakyReLU(0.1, True),
        ]

        self.layers = nn.Sequential(*layers)

    def forward(self, x):
        return (x + self.layers(x))


class DownsampleBlock(nn.Module):
    """ `DownsampleBlock` implements a downsample block.

    Input dimension `dim`. Outputs `2*dim` filters.
    """

    def __init__(self, config, dim):
        super(DownsampleBlock, self).__init__()

        layers = [
            nn.ReflectionPad2d(1),
            nn.Conv2d(
                dim, 2*dim, kernel_size=3, stride=2, padding=0, bias=False
            ),
            nn.BatchNorm2d(2*dim),
            nn.LeakyReLU(0.1, True),
        ]

        self.layers = nn.Sequential(*layers)

    def forward(self, x):
        return self.layers(x)


class YOLOv3(nn.Module):
    def __init__(self, config):
        super(YOLOv3, self).__init__()

        layers = []

        layers.append([
            nn.ReflectionPad2d(1),
            nn.Conv2d(
                3, 32, kernel_size=3, stride=1, padding=0, bias=False
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
            ResidualBlock(config, 256),
        ])

        # layers 36

        layers.append([
            DownsampleBlock(config, 256),
            ResidualBlock(config, 512),
            ResidualBlock(config, 512),
            ResidualBlock(config, 512),
            ResidualBlock(config, 512),
            ResidualBlock(config, 512),
            ResidualBlock(config, 512),
            ResidualBlock(config, 512),
            ResidualBlock(config, 512),

        ])

        # layers 61

        layers.append([
            DownsampleBlock(config, 512),
            ResidualBlock(config, 1024),
            ResidualBlock(config, 1024),
            ResidualBlock(config, 1024),
            ResidualBlock(config, 1024),
        ])

        # layers 74

        yolo1 = [
            nn.Conv2d(
                1024, 512, kernel_size=3, stride=1, padding=0, bias=False
            ),
            nn.BatchNorm2d(32),
            nn.LeakyReLU(0.1, True),
        ]

        self.layers = [nn.Sequential(*l) for l in layers]

    def forward(self, x):
        x0 = self.layers[0](x)
        x1 = self.layers[1](x0)
        x2 = self.layers[2](x1)

        return x2
