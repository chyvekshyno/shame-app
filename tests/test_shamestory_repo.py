from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from shame.main import app
from shame.database import Base, get_database
from shame.repository import ShameStoryRepository
from shame.models import ShameStory, User, Address

from shame import schemas

DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessionTesting = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db_testing():
    db = SessionTesting()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_database] = get_db_testing


@pytest.fixture()
def session() -> Generator[Session, None, None]:
    session = SessionTesting()
    Base.metadata.create_all(bind=engine)

    new_user = User(id=0, username="tuki", password="1111", rating=3)
    lviv_address = Address(
        id=0,
        country="Ukraine",
        state="Lviv",
        city="Lviv",
        street="Hrinchenka, 14a",
    )
    ternopil_address = Address(
        id=3,
        country="Ukraine",
        state="Ternopil",
        city="Ternopil",
        street="Ostrozkiy, 53",
    )

    first_instance: ShameStory = ShameStory(
        id=0,
        author_id=0,
        text="Lorem ipsum dolor sit amet, qui minim labore adipisicing minim sint cillum sint consectetur cupidatat.",
        location_id=0,
    )

    session.add(new_user)
    session.add(lviv_address)
    session.add(ternopil_address)
    session.add(first_instance)
    session.commit()

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def shame_repo() -> ShameStoryRepository:
    repo = ShameStoryRepository()
    return repo


def test_repo_insert_location(session: Session, shame_repo: ShameStoryRepository):
    address = schemas.CreateAddress(
        country="Ukraine",
        state="Vinnytsia",
        city="Vinnytsia",
        street="Roshen st. 5",
    )

    db_address: Address = shame_repo.add_location(session, address)

    assert db_address.id > 0
    assert db_address.country == address.country
    assert db_address.state == address.state
    assert db_address.city == address.city
    assert db_address.street == address.street


def test_repo_insert_shamestory(session: Session, shame_repo: ShameStoryRepository):
    shamestory = schemas.CreateShameStory(
        text="Lorem ipsum dolor sit amet",
        author_id=0,
        location_id=0,
    )

    db_shamestory = shame_repo.add(session=session, shamestory=shamestory)
    check = shame_repo.fetch_by_id(session=session, shamestory_id=db_shamestory.id)

    assert check is not None
    assert check.text == shamestory.text
    assert check.author_id == shamestory.author_id
    assert check.author.username == "tuki"
    assert check.location.country == "Ukraine"
    assert check.location.state == "Lviv"
    assert check.location.city == "Lviv"
    assert check.location.street == "Hrinchenka, 14a"


def test_repo_get_shamestory_by_id(session: Session, shame_repo: ShameStoryRepository):
    id = 0
    text = "Lorem ipsum dolor sit amet, qui minim labore adipisicing minim sint cillum sint consectetur cupidatat."
    author_id = 0

    db_shamestory = shame_repo.fetch_by_id(session=session, shamestory_id=id)

    assert db_shamestory.text == text
    assert db_shamestory.author_id == author_id


def test_repo_get_shamestory_by_author(
    session: Session,
    shame_repo: ShameStoryRepository,
):
    author_id = 0
    text = "Lorem ipsum dolor sit amet, qui minim labore adipisicing minim sint cillum sint consectetur cupidatat."

    db_shamestories = shame_repo.fetch_by_author(session=session, author_id=author_id)

    assert len(db_shamestories) > 0

    example = db_shamestories[0]

    assert example is not None
    assert example.text == text
    assert example.author_id == author_id


def test_repo_get_shamestory_by_location(
    session: Session,
    shame_repo: ShameStoryRepository,
):
    location_id = 0
    text = "Lorem ipsum dolor sit amet, qui minim labore adipisicing minim sint cillum sint consectetur cupidatat."
    author_id = 0

    db_shamestories = shame_repo.fetch_by_location(
        session=session, location_id=location_id
    )

    assert len(db_shamestories) > 0

    example = db_shamestories[0]

    assert example is not None
    assert example.text == text
    assert example.author_id == author_id
    assert example.location_id == location_id
    assert example.location.city == "Lviv"
    assert example.location.street == "Hrinchenka, 14a"


def test_repo_get_shamestories(session: Session, shame_repo: ShameStoryRepository):
    for i in range(30):
        shame_repo.add(
            session,
            schemas.CreateShameStory(text="Lo Ho" * i, author_id=0, location_id=0),
        )

    results = shame_repo.fetch(session, skip=0, limit=20)
    assert len(results) == 20

    example = results[8]
    assert example.author.username == "tuki"
    assert example.location.street == "Hrinchenka, 14a"


def test_repo_update_shamestory(session: Session, shame_repo: ShameStoryRepository):
    """Check updating shamestory though repository"""

    # get instance from db
    id = 0
    db_shamestory = shame_repo.fetch_by_id(session=session, shamestory_id=id)
    assert db_shamestory is not None

    # create updated values
    new_text = (
        "Reprehenderit nostrud nostrud ipsum Lorem est aliquip amet voluptate voluptate"
    )
    new_location = schemas.CreateAddress(
        country="Ukraine", state="Lviv", city="Lviv", street="Sychiv, 22"
    )
    db_location = shame_repo.add_location(session, new_location)
    updated = schemas.ShameStory(
        id=db_shamestory.id,
        author_id=0,
        text=new_text,
        location_id=db_location.id,
    )

    # update though repository
    shame_repo.update(session=session, values=updated)

    # get updated value again
    db_shamestory = shame_repo.fetch_by_id(session=session, shamestory_id=id)

    assert db_shamestory is not None
    assert db_shamestory.text == new_text
    assert db_shamestory.location.city == new_location.city
    assert db_shamestory.location.street == new_location.street


def test_repo_delete_shamestory(session: Session, shame_repo: ShameStoryRepository):
    id = 0
    to_delete = shame_repo.fetch_by_id(session=session, shamestory_id=id)
    assert to_delete is not None

    shame_repo.delete(session=session, shamestory_id=id)

    with pytest.raises(NoResultFound):
        shame_repo.fetch_by_id(session=session, shamestory_id=id)
