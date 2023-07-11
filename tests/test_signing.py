import pytest
from safemodels.cosign import Cosign


def test_sign():
    cosign = Cosign()
    assert cosign.sign("hello") is not None


def test_verify():
    cosign = Cosign()
    assert cosign.verify("hello", cosign.sign("hello")) is True
    assert cosign.verify("hello", cosign.sign("world")) is False
