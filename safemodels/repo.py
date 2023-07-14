from functools import cached_property, lru_cache
import io
from pathlib import Path
import shutil
from typing import ClassVar, NamedTuple, Union
from subprocess import run
import yaml
from threading import Lock

from safemodels.model import Hash, NoHashInDatabase


class Issuer(NamedTuple):
    issuer: str = ".*"
    identity: str = ".*"


Issuers = list[Issuer]


class HashRepo:
    REPO = "yasyf/safemodels"
    TAG = "main"
    HASH_DIR = Path.home() / ".config" / ".safemodels" / "hashes"

    allowed_issuers: ClassVar[Issuers] = [Issuer()]

    @classmethod
    def check(cls, hash: Hash, sig: str):
        return any(
            hash.verify(sig, issuer=issuer, identity=identity)
            for issuer, identity in cls.allowed_issuers
        )

    @classmethod
    @property
    def default(cls):
        if not cls.HASH_DIR.exists():
            return cls.from_github()
        return cls(cls.HASH_DIR)

    @classmethod
    def from_github(cls, repo: str = REPO, tag: str = TAG):
        cls.HASH_DIR.parent.mkdir(parents=True, exist_ok=True)
        if not cls.HASH_DIR.exists():
            run(["git", "clone", f"https://github.com/{repo}.git", cls.HASH_DIR])
        else:
            run(["git", "fetch"], cwd=cls.HASH_DIR)
        run(["git", "checkout", tag], cwd=cls.HASH_DIR)
        return cls(cls.HASH_DIR)

    def __init__(self, dir: Union[str, Path]):
        self.dir = Path(dir)
        self.lock = Lock()

    def _models(self, root=None):
        root = root or self.dir
        for path in root.iterdir():
            if path.is_dir():
                yield from self._models(path)
            elif path.suffix == ".yaml":
                yield path

    def _write(self, hash: Hash):
        path = (self.dir / hash.name).with_suffix(".yml")
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
        with path.open("a") as f:
            f.seek(0, io.SEEK_END)
            yaml.safe_dump(hash.model_dump(), f)

    @cached_property
    def versions(self):
        return {
            (hash.name, hash.version): hash
            for path in self._models()
            for data in yaml.safe_load_all(path.read_text())
            for obj in data
            for hash in [Hash.model_validate(obj)]
        }

    @lru_cache
    def get(self, name, version):
        try:
            return self.versions[(name, version)]
        except KeyError:
            raise NoHashInDatabase(
                f"Hash for model {name}, version {version} not found"
            )

    def set(self, name, version, hash):
        with self.lock:
            self.versions[(name, version)] = Hash(name=name, version=version, hash=hash)
            self._write(self.versions[(name, version)])

    def clear(self):
        with self.lock:
            self.versions.clear()
            shutil.rmtree(self.dir)
