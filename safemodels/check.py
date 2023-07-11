from functools import wraps
from safetensors import safe_open as _safe_open
import warnings

from safemodels.model import NoHashInDatabase, HashMissing, HashMismatch
from safemodels.repo import HashRepo


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


def _check(name: str, hash: int, version: str = "main"):
    try:
        check = HashRepo.default.get(name, version)
    except NoHashInDatabase:
        HashRepo.default.set(name, hash, version)
        warnings.warn(
            f"Hash for {name} ({version}) not found in database. Adding for future."
        )
    else:
        if str(hash) != check.hash:
            warnings.warn(f"Hash mismatch for {name} ({version})")
            raise HashMismatch()


@try_
def check(name: str, hash: int, version: str = "main"):
    _check(name, hash, version)
