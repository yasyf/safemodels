from .hash import safe_hash
from .patch import safe_open, hf_hub_download, install, uninstall
from .check import check
from .cosign import Cosign
from .repo import HashRepo, Issuers, Issuer


def init(allowed_issuers: Issuers):
    HashRepo.allowed_issuers = allowed_issuers
