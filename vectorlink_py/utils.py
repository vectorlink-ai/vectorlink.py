import ctypes
import torch


def torch_type_to_ctype(torch_type):
    if torch_type == torch.float32:
        return ctypes.c_float
    else:
        raise Exception(f"Unrecognized torch type: {torch_type}")


def name_to_torch_type(name: str):
    if name == "float32":
        return torch.float32
    else:
        raise Exception(f"Unrecognized type name: {name}")
