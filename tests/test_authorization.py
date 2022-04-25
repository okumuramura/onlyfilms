from http import HTTPStatus

from fastapi.testclient import TestClient


def test_register(client: TestClient, fake_db, unregister_user):
    response = client.post('/api/register', json=unregister_user)
    assert response.status_code == HTTPStatus.ACCEPTED


def test_invalid_register(client: TestClient, fake_db, invalid_user):
    response = client.post('/api/register', json=invalid_user)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_registered_register(client: TestClient, fake_db, register_user):
    response = client.post('/api/register', json=register_user)
    assert response.status_code == HTTPStatus.NOT_ACCEPTABLE


def test_unregistered_login(client: TestClient, fake_db, unregister_user):
    response = client.post('/api/login', json=unregister_user)
    assert response.status_code == HTTPStatus.NOT_ACCEPTABLE


def test_registered_login(client: TestClient, fake_db, register_user):
    response = client.post('/api/login', json=register_user)
    assert response.status_code == HTTPStatus.ACCEPTED
