from typing import Optional
import torch
import torch.nn.functional as F
from torch.nn.modules.dropout import _DropoutNd
from oslo.torch.distributed import ParallelContext

from oslo.torch.nn.modules.functional import (
    fused_bias_dropout,
)


class FusedBiasDropout(_DropoutNd):
    def forward(self, input: torch.Tensor, bias: torch.Tensor) -> torch.Tensor:
        return fused_bias_dropout(input, bias, self.p, self.training, self.inplace)
