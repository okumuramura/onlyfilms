from http import HTTPStatus

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from pytest_mock import MockerFixture

from onlyfilms.models.orm import Review, Token
from onlyfilms import manager


def test_clear_films_request(client: TestClient, fake_db, fake_films):
    response = client.get('/api/films')

    assert response.status_code == HTTPStatus.OK

    data = response.json()

    assert data['total'] == 10
    assert len(data['films']) == 10


def test_films_request_with_query(client: TestClient, fake_db):
    response = client.get('/api/films?q=%232')  # ?q=#2

    assert response.status_code == HTTPStatus.OK

    data = response.json()

    assert len(data['films']) == 1
    assert data['films'][0]['title'] == 'film #2'
    assert data['total'] == 1


def test_films_request_with_limit_and_offset(client: TestClient, fake_db):
    response = client.get('/api/films?offset=5&limit=2')

    assert response.status_code == HTTPStatus.OK

    data = response.json()

    assert len(data['films']) == 2
    assert data['total'] == 10
    assert data['films'][0]['title'] == 'film #5'


def test_specific_film(client: TestClient, fake_db, fake_films):
    response = client.get('/api/films/1')

    assert response.status_code == HTTPStatus.OK

    data = response.json()

    assert data['title'] == 'film #0'


def test_not_found_film(client: TestClient, fake_db):
    response = client.get('/api/films/666')

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_unauthorized_review(client: TestClient, fake_db, fake_films):
    body = {'text': 'test review', 'score': 6}
    response = client.post('/api/films/1/review', json=body)

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_bad_review(
    client: TestClient, fake_db, fake_films, valid_user_token: str
):
    body = {'text': 'bad review', 'score': -10}
    header = {'authorization': valid_user_token}
    response = client.post('/api/films/1/review', json=body, headers=header)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_ok_review(
    client: TestClient,
    test_db,
    fake_db,
    fake_films,
    register_user,
    valid_user_token: str,
):
    body = {'text': 'this review is ok', 'score': 10}
    header = {'authorization': valid_user_token}
    response = client.post('/api/films/1/review', json=body, headers=header)

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()

    assert data.get('review_id', None) is not None

    review_id: int = data.get('review_id')

    with test_db() as session:
        session: Session
        session.query(Review).filter(Review.id == review_id).delete()
        session.commit()
    # TODO check review exists


def test_not_found_review(
    client: TestClient,
    fake_db,
    fake_films,
    register_user,
    valid_user_token: str,
):
    body = {'text': 'this review on not exists film', 'score': 9}
    header = {'authorization': valid_user_token}
    response = client.post('/api/films/666/review', json=body, headers=header)

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_invalid_token_access(client: TestClient, fake_db, fake_films):
    body = {'test': 'review with invalid token', 'score': 1}
    header = {'authorization': 'invalid_token'}
    response = client.post('/api/films/1/review', json=body, headers=header)

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_film_score(client: TestClient, fake_db, fake_reviews):
    response = client.get('/api/films/1')

    assert response.status_code == HTTPStatus.OK

    data = response.json()

    assert data['score'] == 9.0
    assert data['evaluators'] == 10


def test_getting_reviews(client: TestClient, fake_db, fake_reviews):
    response = client.get('/api/films/1/reviews')

    assert response.status_code == HTTPStatus.OK

    data = response.json()

    assert data['total'] == 10
    assert len(data['reviews']) == 10
    assert data['offset'] == 0
    assert data['reviews'][0]['text'] == 'test review #0'
    assert data['reviews'][0]['author']['login'] == 'test_user_0'


def test_getting_reviews_with_limit_and_offset(
    client: TestClient, fake_db, fake_reviews
):
    response = client.get('/api/films/1/reviews?limit=3&offset=3')

    assert response.status_code == HTTPStatus.OK

    data = response.json()

    assert data['total'] == 10
    assert data['offset'] == 3
    assert len(data['reviews']) == 3
    assert data['reviews'][0]['text'] == 'test review #3'


def test_getting_specific_review(client: TestClient, fake_db, fake_reviews):
    response = client.get('/api/films/1/reviews/1')

    assert response.status_code == HTTPStatus.OK

    data = response.json()
    review = fake_reviews[0]

    assert data['id'] == 1
    assert data['film_id'] == 1
    assert data['text'] == review.text
    assert data['author']['login'] == 'test_user_0'


def test_getting_not_exists_review(client: TestClient, fake_db, fake_reviews):
    response = client.get('/api/films/1/reviews/666')

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_review(
    mocker: MockerFixture,
    client: TestClient,
    fake_db,
    fake_reviews,
    fake_users_tokens,
):
    deleter = mocker.patch('onlyfilms.manager.delete_review')
    deleter.return_value = 1

    token: Token = fake_users_tokens[0]
    header = {'authorization': token.token}

    response = client.delete('/api/films/1/reviews/1', headers=header)

    assert response.status_code == HTTPStatus.OK
    deleter.assert_called_once()


def test_delete_someone_else_review(
    mocker: MockerFixture,
    client: TestClient,
    fake_db,
    fake_reviews,
    fake_users_tokens,
):
    deleter = mocker.spy(manager, 'delete_review')
    deleter.return_value = 1

    token: Token = fake_users_tokens[2]
    header = {'authorization': token.token}

    response = client.delete('/api/films/1/reviews/1', headers=header)

    assert response.status_code == HTTPStatus.FORBIDDEN
    deleter.assert_called_once()
