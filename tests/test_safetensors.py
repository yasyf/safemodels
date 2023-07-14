from safemodels.hash import safe_hash
from safemodels.model import Hash, HashMissing
import pytest
from safemodels.utils.safetensors import extract_metadata


def test_no_hash(sf_filename):
    with pytest.raises(HashMissing):
        Hash.from_safetensor(sf_filename)


def test_rewrite(sf_filename):
    hash = Hash(name="gpt2", version="main", hash=str(safe_hash(sf_filename)))
    hash.sign_safetensor(sf_filename)
    assert hash.model_dump().items() <= extract_metadata(sf_filename).items()
    assert Hash.from_safetensor(sf_filename) == hash
