# `safemodels`
### Cryptographically-secure proof-of-concept for verifying the provenance of ML models.

This library is a thought experiment into what securing the supply chain of ML models could look like. It's built on top of `safetensors`. You should probably read [the blog post](https://musings.yasyf.com/on-llm-supply-chain-attacks/) for more context!

## Installation

```shell
$ pip install safemodels
```

## Usage

### Hashing

```python
from safemodels import safe_hash
from huggingface_hub import hf_hub_download as dl

st = dl("gpt2", filename="model.safetensors")
pt = dl("gpt2", filename="pytorch_model.bin")

assert safe_hash(st) == safe_hash(pt) == 'd6c60a3126ef088e5f8fdaa332da56d552da966a'
```

### Signing

```python
from safemodels import SafeModel
from huggingface_hub import hf_hub_download as dl

st = dl("gpt2", filename="model.safetensors")
sm = SafeModel.from_safetensor(st)
# or
st, sm = SafeModel.from_hf("gpt2", version="main")

sm.sign_safetensor(st) # backwards-compatible rewrite of file
```

### Verification

```pycon
>>> from safemodels import init, Issuer
>>> from huggingface_hub import hf_hub_download
>>>
>>> init(Issuer(identity="EleutherAI", issuer="https://auth.huggingface.com")
>>>
>>> hf_hub_download("EleuterAI/gpt-j-6B", filename="model.safetensors")
Downloading model.safetensors: 100%|███| 548M/548M [00:14<00:00, 39.2MB/s]
211it [00:00, 4785.46it/s]
Error: none of the expected identities matched what was in the certificate, got subjects [EleuterAI] with issuer https://auth.huggingface.com
Traceback (most recent call last):
  ...
safemodels.InvalidSignature: Loaded a safetensor with an invalid signature!
```

### `safetensor` Metadata

```python
from safemodels.utils.safetensors import extract_metadata, update_meta
from huggingface_hub import hf_hub_download as dl

st = dl("gpt2", filename="model.safetensors")

print(extract_metadata(st))
# {'format': 'pt'}

update_meta(st, {"hello": "world"})

print(extract_metadata(st))
# {'format': 'pt', 'hello': 'world'}
```
