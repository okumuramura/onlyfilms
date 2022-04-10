import pytest

from fastapi.testclient import TestClient

from onlyfilms.__main__ import create_app


@pytest.fixture(scope='session')
def client():
    return TestClient(create_app())
