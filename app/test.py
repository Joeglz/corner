from fastapi.testclient import TestClient
import pytest
from .main import app

import asyncio
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from .main import app, create_token
from .models import User

from tortoise.contrib.test import finalizer, initializer

import jwt

@pytest.fixture(scope="module")
def client() -> Generator:
    initializer(["models"])
    with TestClient(app) as c:
        yield c
    finalizer()

@pytest.fixture(scope="module")
def event_loop(client: TestClient) -> Generator:
    yield client.task.get_loop()


def test_create_user(client: TestClient, event_loop: asyncio.AbstractEventLoop):
    
    response = client.post("/users", json={"username": "test4", "password_hash": "test"})
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == "test3"
    assert "id" in data
    user_id = data["id"]

    async def get_user_by_db():
        user = await User.get(id=user_id)
        return user

    user_obj = event_loop.run_until_complete(get_user_by_db())
    assert user_obj.id == user_id

def test_get_token(client: TestClient): 
    response = client.post("/token", data={"username": "admin", "password": "root"})
    assert response.status_code == 200, response.text
    data = response.json()

    assert "access_token" in data
    assert "token_type" in data

def test_data(client: TestClient): 

    user_encode = {
        'id' : 1,
        'username' : 'admin'
    }

    token = jwt.encode(user_encode, 'corner2021' )

    headers = {
        'Authorization': 'Bearer {}'.format(token)
    }

    print(headers)

    response = client.get("/data", headers=headers)

    print(response)

    data = response.json()

    assert "rates" in data
    assert "provider_1" in data['rates']
    assert "value" in data['rates']['provider_1']
    assert "last_updated" in data['rates']['provider_1']

    assert "provider_2" in data['rates']
    assert "value" in data['rates']['provider_2']
    assert "last_updated" in data['rates']['provider_2']
    
    assert "provider_3" in data['rates']
    assert "value" in data['rates']['provider_3']
    assert "last_updated" in data['rates']['provider_3']


