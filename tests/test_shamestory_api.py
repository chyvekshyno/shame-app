from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from shame import models, schemas, repository as repo
from shame.database import Base, get_database
from shame.main import app


SQLITE_DB_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLITE_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

SessionTesting = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base.metadata.create_all(bind=engine)


def get_db_testing():
    db = SessionTesting()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_database] = get_db_testing

client = TestClient(app)


def startup():
    models.Base.metadata.create_all(bind=engine)
    db = SessionTesting()

    # Add initial data
    repo.add_user(
        db,
        schemas.CreateUser(
            email="tuky.chyvekshyno@gmail.com", username="tuki", password="1111"
        ),
    )
    repo.add_location(
        db,
        schemas.CreateAddress(
            country="Ukraine", state="Lviv", city="Lviv", street="Hrinchenka, 14a"
        ),
    )
    repo.add(
        db,
        schemas.CreateShameStory(
            text="Lorem ipsum dolor sit amet, qui minim labore adipisicing.",
            author_id=0,
            location_id=0,
        ),
    )
    db.close()


startup()


def test_api_runs():
    responce = client.get("/")
    assert responce.status_code == 200
    assert responce.json() == {"msg": "Hello Shame Application!"}


def test_post_shamestory():
    responce = client.post(
        "/shamestories/",
        json={
            "text": "Lorem ipsum dolor sit amet, qui minim.",
            "author_id": 0,
            "location_id": 0,
        },
    )
    assert responce.status_code == 200
    responce_result = responce.json()
    assert responce_result["text"] == "Lorem ipsum dolor sit amet, qui minim."


def test_get_shamestories():
    responce = client.get("/shamestories")
    assert responce.status_code == 200

    responce_result = responce.json()
    item_1 = responce_result[0]
    assert item_1["text"] == "Lorem ipsum dolor sit amet, qui minim labore adipisicing."
    assert item_1["author_id"] == 0


def test_get_shamestory_by_id():
    shamestory_id = 1
    responce = client.get(f"/shamestories/{shamestory_id}")
    assert responce.status_code == 200


# def test_get_shamestories_by_location():
#     location = schemas.CreateAddress(
#         country="Ukraine",
#         state="Lviv",
#         city="Lviv",
#         street="Hrinchenka, 14a",
#     )
#
#     responce = client.get("/shamestories/")
#     assert responce.status_code == 200


# def test_get_shamestories_by_user():
#     user_id = 0
#     responce = client.get(f"/user/{user_id}/shamestories")
#     assert responce.status_code == 200


def test_update_shamestory_text():
    shamestory_id = 1
    responce = client.put(
        url=f"/shamestories/{shamestory_id}",
        json={
            "author_id": 0,
            "location_id": 0,
            "text": "New Lorem ipsum text",
        },
    )
    assert responce.status_code == 200

    result = responce.json()
    assert result["text"] == "New Lorem ipsum text"


def test_delete_shamestory():
    shamestory_id = 1
    responce = client.delete(f"/shamestories/{shamestory_id}")
    with pytest.raises(NoResultFound):
        found = client.get(f"/shamestories/{shamestory_id}")
        assert found is None
