from http import HTTPStatus

from fastapi.testclient import TestClient


def test_admin(client: TestClient):
    response = client.get('onlyfilms/admin')
    assert response.status_code == HTTPStatus.OK
