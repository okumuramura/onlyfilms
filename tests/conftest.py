import pytest

from fastapi.testclient import TestClient

from onlyfilms.__main__ import create_app


@pytest.fixture(scope='session')
def app():
    return create_app()


@pytest.fixture(scope='session')
def client(app):
    return TestClient(app)
