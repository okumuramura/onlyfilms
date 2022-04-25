import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pytest_mock import MockerFixture

from onlyfilms import Base
from onlyfilms.__main__ import create_app


@pytest.fixture(scope='session')
def test_db():
    if os.path.exists('.test.db'):
        os.remove('.test_db')

    engine = create_engine('sqlite:///test.db')
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)
    yield TestSession


@pytest.fixture(scope='session')
def fake_db(test_db, session_mocker: MockerFixture):
    session_mocker.patch('onlyfilms.Session', test_db)
    session_mocker.patch('onlyfilms.manager.SessionCreator', test_db)
    session_mocker.patch('onlyfilms.api.Session', test_db)


@pytest.fixture(scope='session')
def client():
    return TestClient(create_app())
