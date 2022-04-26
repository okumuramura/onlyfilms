import os

import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from onlyfilms import Base
from onlyfilms.__main__ import create_app
from onlyfilms.models.orm import Film, Review, Token, User


@pytest.fixture(scope='session')
def test_db():
    if os.path.exists('./test.db'):
        os.remove('./test.db')

    engine = create_engine('sqlite:///test.db')
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine, expire_on_commit=False)
    yield TestSession
    os.remove('./test.db')


@pytest.fixture(scope='session')
def fake_db(test_db, session_mocker: MockerFixture):
    session_mocker.patch('onlyfilms.Session', test_db)
    session_mocker.patch('onlyfilms.manager.SessionCreator', test_db)
    session_mocker.patch('onlyfilms.api.Session', test_db)


@pytest.fixture(scope='session')
def client():
    return TestClient(create_app())


@pytest.fixture(scope='session')
def register_user(test_db, fake_db):
    data = {'login': 'test_user', 'password': 'test_password'}
    with test_db() as session:
        new_user = User(login=data['login'], password=data['password'])
        session.add(new_user)
        session.commit()
    return data


@pytest.fixture(scope='session')
def valid_user_token(test_db, fake_db, register_user):
    with test_db() as session:
        session: Session
        user: User = (
            session.query(User)
            .filter(User.login == register_user['login'])
            .first()
        )
        token = Token(user)
        token_str = token.token
        session.add(token)
        session.commit()

    return token_str


@pytest.fixture
def unregister_user(test_db, fake_db):
    data = {'login': 'unreg_user', 'password': 'some_password'}
    with test_db() as session:
        session.query(User).filter(User.login == data['login']).delete()
        session.commit()
    return data


@pytest.fixture(scope='session')
def invalid_user():
    return {'login': 'very_long_login_wooow', 'password': 'psd'}


@pytest.fixture(scope='session')
def fake_films(test_db):
    films = [Film(f'film #{x}') for x in range(10)]
    with test_db() as session:
        session: Session
        session.add_all(films)
        session.commit()

    return films


@pytest.fixture(scope='session')
def fake_users(test_db):
    users = [User(f'test_user_{x}', 'password') for x in range(10)]
    with test_db() as session:
        session: Session
        session.add_all(users)
        session.commit()

    return users


@pytest.fixture
def clear_reviews(test_db):
    with test_db() as session:
        session: Session
        session.query(Review).delete()


@pytest.fixture(scope='session')
def fake_reviews(test_db, fake_films, fake_users):
    reviews = []
    fake_film = fake_films[0]
    for i, user in enumerate(fake_users):
        reviews.append(Review(user, fake_film, f'test review #{i}', score=9))

    with test_db() as session:
        session: Session
        session.add_all(reviews)
        session.commit()

    return reviews


@pytest.fixture(scope='session')
def fake_users_tokens(test_db, fake_users):
    tokens = [Token(user) for user in fake_users]

    with test_db() as session:
        session: Session
        session.add_all(tokens)
        session.commit()

    return tokens


@pytest.fixture
def deleted_review(test_db, fake_users, fake_films):
    author: User = fake_users[0]
    film: Film = fake_films[5]

    with test_db() as session:
        session: Session
        review = Review(author, film, 'deleted review')
        session.add(review)
        session.commit()

    review_id = review.id

    yield review

    with test_db() as session:
        session.query(Review).filter(Review.id == review_id).delete()
        session.commit()
