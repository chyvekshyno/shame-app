from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from shame import schemas, repository
from shame.database import Base
from shame.models import Address, ShameStory
from shame.auth.models import User


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
def session() -> Generator[Session, None, None]:
    session = SessionTesting()
    Base.metadata.create_all(bind=engine)

    new_user = User(
        id=0,
        email="tuky.chyvekshyno@gmail.com",
        username="tuki",
        password_hashed="1111",
        rating=3,
    )
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
        title="Lorem Ipsum",
        text="Lorem ipsum dolor sit amet, qui minim labore adipisicing minim sint cillum sint consectetur cupidatat.",
        author_id=0,
        address_id=0,
    )

    session.add(new_user)
    session.add(lviv_address)
    session.add(ternopil_address)
    session.add(first_instance)
    session.commit()

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)


def test_repo_insert_address(session: Session):
    address = schemas.CreateAddress(
        country="Ukraine",
        state="Vinnytsia",
        city="Vinnytsia",
        street="Roshen st. 5",
    )

    db_address: Address = repository.add_address(session, address)

    assert db_address.id > 0
    assert db_address.country == address.country
    assert db_address.state == address.state
    assert db_address.city == address.city
    assert db_address.street == address.street


def test_repo_insert_shamestory(session: Session):
    shamestory = schemas.CreateShameStory(
        title="Lorem Short",
        text="Lorem ipsum dolor sit amet.",
    )

    db_shamestory = repository.add(
        db=session,
        shamestory=shamestory,
        author_id=0,
        address_id=0,
    )
    check = repository.get_by_id(db=session, shamestory_id=db_shamestory.id)

    assert check is not None
    assert check.text == shamestory.text
    assert check.title == shamestory.title
    assert check.author_id == 0
    assert check.author.username == "tuki"
    assert check.address.country == "Ukraine"
    assert check.address.state == "Lviv"
    assert check.address.city == "Lviv"
    assert check.address.street == "Hrinchenka, 14a"


def test_repo_get_shamestory_by_id(session: Session):
    id = 0
    text = "Lorem ipsum dolor sit amet, qui minim labore adipisicing minim sint cillum sint consectetur cupidatat."
    author_id = 0

    db_shamestory = repository.get_by_id(db=session, shamestory_id=id)

    assert db_shamestory.text == text
    assert db_shamestory.author_id == author_id


def test_repo_get_shamestory_by_author(session: Session):
    author_id = 0
    text = "Lorem ipsum dolor sit amet, qui minim labore adipisicing minim sint cillum sint consectetur cupidatat."

    db_shamestories = repository.get_by_author(db=session, author_id=author_id)

    assert len(db_shamestories) > 0

    example = db_shamestories[0]

    assert example is not None
    assert example.text == text
    assert example.author_id == author_id


def test_repo_get_shamestory_by_address(session: Session):
    address_id = 0
    text = "Lorem ipsum dolor sit amet, qui minim labore adipisicing minim sint cillum sint consectetur cupidatat."
    author_id = 0

    db_shamestories = repository.get_by_address(db=session, address_id=address_id)

    assert len(db_shamestories) > 0

    example = db_shamestories[0]

    assert example is not None
    assert example.text == text
    assert example.author_id == author_id
    assert example.address_id == address_id
    assert example.address.city == "Lviv"
    assert example.address.street == "Hrinchenka, 14a"


def test_repo_get_shamestories(session: Session):
    for i in range(30):
        repository.add(
            session,
            schemas.CreateShameStory(title="P" * i, text="Lo Ho" * i),
            author_id=0,
            address_id=0,
        )

    results = repository.get(session, skip=0, limit=20)
    assert len(results) == 20

    example = results[8]
    assert example.author.username == "tuki"
    assert example.address.street == "Hrinchenka, 14a"


def test_repo_update_shamestory(session: Session):
    """Check updating shamestory though repository"""

    # get instance from db
    id = 0
    db_shamestory = repository.get_by_id(db=session, shamestory_id=id)
    assert db_shamestory is not None

    # create updated values
    updated = schemas.CreateShameStory(
        title="New Lorem Ipsum", text="Reprehenderit nostrud nostrud ipsum!"
    )

    # update though repository
    repository.update(db=session, shamestory_id=id, values=updated)

    # get updated value again
    db_shamestory = repository.get_by_id(db=session, shamestory_id=id)

    assert db_shamestory is not None
    assert db_shamestory.text == updated.text
    assert db_shamestory.title == updated.title


def test_repo_delete_shamestory(session: Session):
    id = 0
    to_delete = repository.get_by_id(db=session, shamestory_id=id)
    assert to_delete is not None

    repository.delete(db=session, shamestory_id=id)

    with pytest.raises(NoResultFound):
        repository.get_by_id(db=session, shamestory_id=id)
