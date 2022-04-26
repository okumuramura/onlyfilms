from http import HTTPStatus

from pytest_mock import MockerFixture

from onlyfilms import manager


def test_get_films(fake_db, fake_films):
    result, total = manager.get_films()

    assert len(result) == 10
    assert total == 10


def test_wrapper_with_session(mocker: MockerFixture, fake_db):

    fake_function_mock = mocker.Mock()

    orm_func = manager.orm_function(fake_function_mock)

    orm_func(1, 2, 3, test='test', session='fake_session')

    fake_function_mock.assert_called_once_with(
        1, 2, 3, test='test', session='fake_session'
    )


def test_get_film_score(fake_db, fake_reviews):
    score = manager.get_film_score(1)

    assert score == 9.0


def test_get_user(fake_db, register_user):
    user = manager.get_user(1)

    assert user.login == register_user['login']


def test_post_review_sql_error(fake_db, fake_reviews, fake_users, fake_films):
    user = fake_users[0]
    film = fake_films[0]

    response, id = manager.post_review(film.id, user, 'some text')

    assert response == HTTPStatus.BAD_REQUEST
    assert id is None


def test_delete_review(fake_db, test_db, fake_users, deleted_review):
    author = fake_users[0]
    review_id = deleted_review.id
    deleted = manager.delete_review(review_id, author)

    assert deleted == review_id
