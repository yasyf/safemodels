from pathlib import Path
from typing import Union
from pydantic import BaseModel, ConfigDict
from safemodels import safe_hash
from huggingface_hub import hf_hub_download

from safemodels.utils.safetensors import extract_metadata, update_meta
from safemodels.cosign import Cosign


class SafeModelsError(Exception):
    pass


class HashMissing(SafeModelsError, ValueError):
    def __init__(self) -> None:
        super().__init__("Loaded a safetensor without a hash.")


class HashMismatch(SafeModelsError, ValueError):
    def __init__(self) -> None:
        super().__init__("Loaded a safetensor with a mismatched hash!")


class InvalidSignature(HashMismatch):
    def __init__(self) -> None:
        ValueError.__init__(self, "Loaded a safetensor with an invalid signature!")


class NoHashInDatabase(SafeModelsError, KeyError):
    pass


class Hash(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    version: str
    hash: str

    def sign_safetensor(self, filename: Union[str, Path]):
        sig = Cosign().sign(self.model_dump_json())
        update_meta(filename, {"sig": sig, **self.model_dump()})

    def verify(self, sig: str, **kwargs):
        return Cosign().verify(self.model_dump_json(), sig, **kwargs)

    @classmethod
    def from_safetensor(cls, filename: Union[str, Path]):
        meta = extract_metadata(filename)
        if "hash" not in meta:
            raise HashMissing()
        if meta["hash"] != safe_hash(filename):
            raise HashMismatch()
        return cls(**meta)

    @classmethod
    def from_hf(cls, name: str, version: str, filename: str = "model.safetensors"):
        file = hf_hub_download(name, revision=version, filename=filename)
        return file, cls.from_tensor(name, version, file)

    @classmethod
    def from_tensor(cls, name: str, version: str, filename: Union[str, Path]):
        return cls(name=name, version=version, hash=safe_hash(filename))
