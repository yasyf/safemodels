from huggingface_hub import hf_hub_download as _hf_hub_download
from safemodels import check
from safemodels.hash import safe_hash


def hf_hub_download(repo_id: str, filename: str, **kwargs):
    file = _hf_hub_download(repo_id, filename=filename, **kwargs)
    if filename.endswith(".safetensors"):
        check(repo_id, safe_hash(file), kwargs.get("revision", "main"))
    return file
