from huggingface_hub import hf_hub_download
import pytest


@pytest.fixture
def sf_filename():
    return hf_hub_download("gpt2", filename="model.safetensors", force_download=True)


@pytest.fixture
def tiny_sf_filename():
    return hf_hub_download(
        "hustvl/yolos-tiny", filename="model.safetensors", force_download=True
    )


@pytest.fixture
def pt_filename():
    return hf_hub_download("gpt2", filename="pytorch_model.bin")
