from typing import Tuple, List

import torch
import torch.nn as nn

from oslo.transformers.modeling_utils import OsloModel


class ParallelWrapper(nn.Module):
    """Marker interface"""


def is_huggingface_model(model):
    try:
        import transformers

        return isinstance(model, transformers.PreTrainedModel)
    except ImportError:
        return False


def is_oslo_model(model):
    if isinstance(model, OsloModel):
        return True

    for module in model.modules():
        if isinstance(module, OsloModel):
            return True
    return False


def is_wrapper(model):
    if isinstance(model, ParallelWrapper):
        return True

    for module in model.modules():
        if isinstance(module, ParallelWrapper):
            return True
    return False


def unwrap_parallel(model):
    while isinstance(model, ParallelWrapper):
        model = model.module
    return model


def get_parameter_dtype(parameter: nn.Module):
    try:
        return next(parameter.parameters()).dtype
    except StopIteration:
        # For nn.DataParallel compatibility in PyTorch 1.5

        def find_tensor_attributes(module: nn.Module) -> List[Tuple[str, torch.Tensor]]:
            tuples = [(k, v) for k, v in module.__dict__.items() if torch.is_tensor(v)]
            return tuples

        gen = parameter._named_members(get_members_fn=find_tensor_attributes)
        first_tuple = next(gen)
        return first_tuple[1].dtype


def allocate_params(model, parallel_context):
    for name, parameter in model.named_parameters():
        if hasattr(parameter, "oslo_parallel"):
            device = parallel_context.ranks2device(parameter.oslo_parallel)
            parameter.to(f"cuda:{device}")
