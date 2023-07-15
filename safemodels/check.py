from functools import wraps
from safetensors import safe_open as _safe_open
import warnings

from safemodels.model import (
    Hash,
    InvalidSignature,
    NoHashInDatabase,
    HashMissing,
    HashMismatch,
)
from safemodels.hash import safe_hash
from safemodels.repo import HashRepo
from safemodels.utils.safetensors import extract_metadata


def try_(fn):
    @wraps(fn)
    def wrapped(*args, throw: bool = False, **kwargs):
        try:
            return fn(*args, **kwargs)
        except (HashMissing, NoHashInDatabase) as e:
            warnings.warn(str(e))
        except HashMismatch:
            if throw:
                raise
        except Exception:
            pass

    return wrapped


def _check(name: str, filename: str, version: str = "main"):
    hash = safe_hash(filename)
    meta = extract_metadata(filename)
    if "sig" not in meta:
        warnings.warn(f"Signature missing for {name} ({version})")
    elif not HashRepo.check(Hash(name=name, version=version, hash=hash), meta["sig"]):
        warnings.warn(f"Signature mismatch for {name} ({version})")
        raise InvalidSignature()

    try:
        check = HashRepo.default.get(name, version)
    except NoHashInDatabase:
        HashRepo.default.set(name, hash, version)
        warnings.warn(
            f"Hash for {name} ({version}) not found in database. Adding for future."
        )
    else:
        if hash != check.hash:
            warnings.warn(f"Hash mismatch for {name} ({version})")
            raise HashMismatch()


@try_
def check(name: str, filename: str, version: str = "main"):
    _check(name, filename, version)
