import pytest

from huggingface_hub import hf_hub_download
from safemodels import safe_hash


@pytest.fixture
def sf_filename():
    return hf_hub_download("gpt2", filename="model.safetensors")


@pytest.fixture
def pt_filename():
    return hf_hub_download("gpt2", filename="pytorch_model.bin")


def test_hash(sf_filename, pt_filename):
    sf_hash = hash(sf_filename)
    pt_hash = hash(pt_filename)
    assert sf_hash == pt_hash
