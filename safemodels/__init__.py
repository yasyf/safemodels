from typing import Union
from .hash import safe_hash
from .model import Hash as SafeModel
from .patch import safe_open, hf_hub_download, install, uninstall
from .check import check as check_model
from .cosign import Cosign
from .repo import HashRepo, Issuers, Issuer


def init(allowed_issuers: Union[Issuer, Issuers]):
    HashRepo.allowed_issuers = (
        [allowed_issuers] if isinstance(allowed_issuers, Issuer) else allowed_issuers
    )
