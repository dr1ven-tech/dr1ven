import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F

class ResidualBlock(nn.Module):
    def __init__(self, config, dim):
        super(ResidualBlock, self).__init__()

        layers = [
            nn.Conv2d(
                2*dim, dim, kernel_size=1, stride=1, padding=0, bias=False
            ),
            nn.BatchNorm2d(dim),
            nn.LeakyReLU(0.1, True),
        ]

        layers += [
            nn.ReflectionPad2d(1),
            nn.Conv2d(
                dim, 2*dim, kernel_size=3, stride=1, padding=0, bias=False
            ),
            nn.BatchNorm2d(2*dim),
            nn.LeakyReLU(0.1, True),
        ]


        self.layers = nn.Sequential(*layers)

    def forward(self, x):
        return (x + self.layers(x))
