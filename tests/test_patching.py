import pytest
from safemodels import install, uninstall


@pytest.fixture(autouse=True)
def run_around_tests():
    install()
    yield
    uninstall()
