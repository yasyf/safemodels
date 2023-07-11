from pathlib import Path
from typing import Union
from pydantic import BaseModel, ConfigDict
from safemodels import safe_hash
from huggingface_hub import hf_hub_download
from safemodels.utils.safetensors import extract_metadata, update_meta


class SafeModelsError(Exception):
    pass


class HashMissing(SafeModelsError, ValueError):
    def __init__(self) -> None:
        super().__init__("Loaded a safetensor without a hash.")


class HashMismatch(SafeModelsError, ValueError):
    def __init__(self) -> None:
        super().__init__("Loaded a safetensor with a mismatched hash!")


class NoHashInDatabase(SafeModelsError, KeyError):
    pass


class Hash(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    version: str
    hash: str

    def rewrite_safetensor(self, filename: Union[str, Path]):
        update_meta(filename, self.model_dump())

    @classmethod
    def from_safetensor(cls, filename: Union[str, Path]):
        meta = extract_metadata(filename)
        if "hash" not in meta:
            raise HashMissing()
        if meta["hash"] != str(safe_hash(filename)):
            raise HashMismatch()
        return cls(**meta)

    @classmethod
    def from_hf(cls, name: str, version: str, filename: str = "model.safetensors"):
        file = hf_hub_download(name, revision=version, filename=filename)
        return cls.from_tensor(name, version, file)

    @classmethod
    def from_tensor(cls, name: str, version: str, filename: Union[str, Path]):
        return cls(name=name, version=version, hash=str(safe_hash(filename)))
