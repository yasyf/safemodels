from typing import Generator

import torch, xxhash, os
import numpy as np
from tqdm import tqdm

from safetensors import safe_open


def _hash(arrs: Generator[np.ndarray, None, None]) -> int:
    x = xxhash.xxh64()
    for arr in tqdm(arrs):
        for chunk in np.nditer(arr, flags=["buffered", "external_loop"]):
            x.update(memoryview(chunk))
    return x.intdigest()


def st_hash(filename) -> int:
    with safe_open(filename, framework="np") as f:
        return _hash(f.get_tensor(k) for k in sorted(f.keys()))


def pt_hash(filename) -> int:
    f = torch.load(filename)
    return _hash(f[k] for k in sorted(f.keys()))


def np_hash(filename) -> int:
    f = np.load(filename)
    return _hash(f[k] for k in sorted(f.keys()))


def safe_hash(filename) -> int:
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
