from huggingface_hub import hf_hub_download
import pytest


@pytest.fixture
def sf_filename():
    return hf_hub_download("gpt2", filename="model.safetensors")


@pytest.fixture
def pt_filename():
    return hf_hub_download("gpt2", filename="pytorch_model.bin")
