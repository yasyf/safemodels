import warnings
import pytest
from safemodels import Issuer, install, uninstall, init as sm_init
from safemodels.hash import safe_hash
from safemodels.model import Hash, InvalidSignature
from safemodels.utils.safetensors import update_meta


@pytest.fixture(autouse=True)
def run_around_tests():
    install()
    yield
    uninstall()


@pytest.fixture
def signed_sf_filename(tiny_sf_filename):
    hash = Hash(
        name="hustvl/yolos-tiny", version="main", hash=safe_hash(tiny_sf_filename)
    )
    hash.sign_safetensor(tiny_sf_filename)
    return tiny_sf_filename


def test_safe_open_default(tiny_sf_filename):
    from safetensors import safe_open

    with pytest.warns(Warning, match="without a hash"):
        safe_open(tiny_sf_filename, framework="pt")


def test_safe_open_signed(signed_sf_filename):
    from safetensors import safe_open

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        safe_open(signed_sf_filename, framework="pt")


def test_safe_open_incorrect_name(signed_sf_filename):
    from safetensors import safe_open

    with pytest.raises(InvalidSignature):
        safe_open(signed_sf_filename, framework="pt", name="noop")


def test_safe_open_correct_issuer(signed_sf_filename):
    from safetensors import safe_open

    sm_init([Issuer(issuer=".*github.*")])
    assert safe_open(signed_sf_filename, framework="pt") is not None


def test_safe_open_incorrect_issuer(signed_sf_filename):
    from safetensors import safe_open

    sm_init([Issuer(identity="root")])
    with pytest.raises(InvalidSignature):
        safe_open(signed_sf_filename, framework="pt", throw=True)


def test_safe_open_corrupt_signature(signed_sf_filename):
    from safetensors import safe_open

    update_meta(signed_sf_filename, {"sig": "foobar"})

    with pytest.raises(InvalidSignature):
        safe_open(signed_sf_filename, framework="pt", throw=True)
