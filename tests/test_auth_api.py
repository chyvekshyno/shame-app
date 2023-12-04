from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from shame.auth import repository as user_repo
from shame.auth import schemas
from shame.database import Base, get_database
from shame.app import app


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
    Base.metadata.create_all(bind=engine)
    db = SessionTesting()

    # Add initial data
    new_user = schemas.CreateUser(
        email="tuky.chyvekshyno@gmail.com",
        username="tuki",
        password="1111",
    )

    user_repo.add(db=db, user=new_user)
    db.close()


startup()


# def test_api_user_login():
#     responce = client.post("/login")
#
#     assert responce.status_code == 200
#
# def test_api_get_current_user():
#     responce = client.post("/users/me")
#
#     assert responce.status_code == 200
#
# def test_api_get_user():
#     username = "tuki"
#     responce = client.post(f"/users/{username}")
#
#     assert responce.status_code == 200
#
# def test_api_get_users10():
#     limit = 10
#     responce = client.post(f"/users/?limit={limit}")
#
#     assert responce.status_code == 200
#
#
# # def test_api_get_user_20to30():
# #     assert False
#
#
# # def test_api_get_user_by_username():
# #     assert False
#
#
# # def test_api_get_user_by_email():
# #     assert False
#
#
# def test_api_update_user():
#     update_values = schemas.UserBase(
#         username="tukiNewUsername",
#         full_name="Tuki Chyvekshyno"
#     )
#     responce = client.put("/users/me")
#
#     assert responce.status_code == 200
#
#
# def test_api_delete_user():
#     username = "tuki"
#     responce = client.delete("/users/me")
#     assert responce.status_code == 200
#
#     responce2 = client.get(f"/users/{username}")
#     assert responce.status_code == 404
