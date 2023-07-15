from typing import Generator

import os, hashlib
import numpy as np
from tqdm import tqdm

from safetensors import safe_open


def _hash(arrs: Generator[np.ndarray, None, None]) -> str:
    x = hashlib.blake2b(digest_size=20)
    for arr in tqdm(arrs):
        for chunk in np.nditer(arr, flags=["buffered", "external_loop"]):
            x.update(memoryview(chunk))
    return x.hexdigest()


def st_hash(filename) -> str:
    with safe_open(filename, framework="np") as f:
        return _hash(f.get_tensor(k) for k in sorted(f.keys()))


def pt_hash(filename) -> str:
    import torch

    f = torch.load(filename)
    return _hash(f[k] for k in sorted(f.keys()))


def np_hash(filename) -> str:
    f = np.load(filename)
    return _hash(f[k] for k in sorted(f.keys()))


def safe_hash(filename) -> str:
    ext = os.path.splitext(filename)[1]
    try:
        return {
            ".npz": np_hash,
            ".npy": np_hash,
            ".pt": pt_hash,
            ".bin": pt_hash,
            ".safetensors": st_hash,
        }[ext](filename)
    except KeyError:
        raise ValueError(f"Unknown file format: {ext}")
