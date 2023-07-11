from .huggingface_hub import hf_hub_download
from .safetensors import safe_open
import sys

PATCHES = {
    "huggingface_hub": hf_hub_download,
    "safetensors": safe_open,
}


def install():
    for name, func in PATCHES.items():
        try:
            mod = __import__(name)
        except ImportError:
            pass
        else:
            func.orig = getattr(mod, func.__name__)
            setattr(sys.modules[mod.__name__], func.__name__, func)


def uninstall():
    for name, func in PATCHES.items():
        try:
            mod = __import__(name)
        except ImportError:
            pass
        else:
            setattr(sys.modules[mod.__name__], func.__name__, func.orig)
