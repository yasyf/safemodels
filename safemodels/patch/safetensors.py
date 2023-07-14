from typing import Optional
from safetensors import safe_open as _safe_open

from safemodels.model import Hash
from safemodels.check import try_, _check


@try_
def _check_safetensor(filename: str, name: Optional[str], version: str):
    if not name:
        hash = Hash.from_safetensor(filename)
        name, version = hash.name, hash.version
    _check(name, filename, version)


def safe_open(
    filename: str,
    name: Optional[str] = None,
    version: str = "main",
    throw: bool = False,
    **kwargs
):
    tensor = _safe_open(filename, **kwargs)
    _check_safetensor(filename, name, version, throw=throw)
    return tensor
