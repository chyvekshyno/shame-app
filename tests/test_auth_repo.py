from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from shame.auth import repository, schemas, utils
from shame.auth.models import User
from shame.database import Base


DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessionTesting = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture()
def db() -> Generator[Session, None, None]:
    session = SessionTesting()
    Base.metadata.create_all(bind=engine)

    new_user = User(
        id=0,
        email="tuky.chyvekshyno@gmail.com",
        username="tuki",
        password_hashed="1111",
        rating=3,
    )
    session.add(new_user)
    session.commit()

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)


#################
#     Tests     #
#################


def test_repo_insert_user(db: Session):
    user = schemas.CreateUser(
        email="yyyyyana.ssssshamrai@gmail.com",
        username="Yana",
        password="1234",
    )

    db_user = repository.add(db=db, user=user)

    assert db_user is not None
    assert db_user.id == 1
    assert db_user.username == user.username
    assert db_user.validate_password(user.password)
    assert db_user.email == user.email


def test_repo_get_users10(db: Session):
    email_pattern = "rq"
    for i in range(12):
        repository.add(
            db=db,
            user=schemas.CreateUser(
                username=email_pattern * i,
                email=email_pattern * i + "@gmail.com",
                password="1111",
            ),
        )

    db_users = repository.get(db=db)
    assert db_users is not None
    assert len(db_users) == 10


# def test_repo_get_users20to30(db: Session):
#     assert False


def test_repo_get_user_by_id(db: Session):
    db_user = repository.get_by_id(db=db, id=0)
    assert db_user is not None
    assert db_user.email == "tuky.chyvekshyno@gmail.com"
    assert db_user.username == "tuki"
    assert db_user.password_hashed == "1111"
    assert db_user.rating == 3


def test_repo_get_user_by_email(db: Session):
    db_user = repository.get_by_email(db=db, email="tuky.chyvekshyno@gmail.com")
    assert db_user is not None
    assert db_user.email == "tuky.chyvekshyno@gmail.com"
    assert db_user.username == "tuki"
    assert db_user.password_hashed == "1111"
    assert db_user.rating == 3


def test_repo_get_user_by_username(db: Session):
    db_user = repository.get_by_username(db=db, username="tuki")
    assert db_user is not None
    assert db_user.email == "tuky.chyvekshyno@gmail.com"
    assert db_user.username == "tuki"
    assert db_user.password_hashed == "1111"
    assert db_user.rating == 3


def test_repo_update_user(db: Session):
    db_user = repository.get_by_id(db=db, id=0)
    assert db_user is not None
    assert db_user.email == "tuky.chyvekshyno@gmail.com"
    assert db_user.username == "tuki"
    assert db_user.full_name is None
    assert db_user.password_hashed == "1111"
    assert db_user.rating == 3

    new_db_user = repository.update(db=db, id=0, values=schemas.UserBase(
        username="tukiNew",
        full_name="Artur Onyshkevych"
    ))
    
    assert new_db_user is not None
    assert new_db_user.email == "tuky.chyvekshyno@gmail.com"
    assert new_db_user.username == "tukiNew"
    assert new_db_user.full_name == "Artur Onyshkevych"
    assert new_db_user.password_hashed == "1111"
    assert new_db_user.rating == 3


def test_repo_delete_user(db: Session):
    db_user = repository.get_by_id(db=db, id=0)
    assert db_user is not None
    assert db_user.email == "tuky.chyvekshyno@gmail.com"
    assert db_user.username == "tuki"

    repository.delete(db=db, id=db_user.id)
    with pytest.raises(NoResultFound):
        db_user = repository.get_by_id(db=db, id=0)
        assert db_user is None
