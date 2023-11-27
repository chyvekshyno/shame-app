from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.sql import delete, select, update

from shame.database import Base, get_database
from shame.main import app
from shame.models import Address, ShameStory, User

DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    DATABASE_URL,
    # echo=True,
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
        id=0, country="Ukraine", state="Lviv", city="Lviv", street="Hrinchenka, 14a"
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
        # attachments=["path/to/some/interesting/photo"],
    )

    session.add(new_user)
    session.add(lviv_address)
    session.add(ternopil_address)
    session.add(first_instance)
    session.commit()

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)


def test_db_add_new_author(session: Session):
    new_user = User(id=1, username="rostik", password="2222", rating=0)
    session.add(new_user)
    session.commit()
    user = session.scalars(select(User).where(User.username == "rostik")).first()
    assert user is not None
    assert user.username == new_user.username


def test_db_add_shamestory(session: Session):
    kyiv_address = Address(
        id=1, country="Ukraine", state="Kyiv", city="Kyiv", street="Vassylkivska, 5"
    )

    adding_shamestory = ShameStory(
        id=3,
        author_id=0,
        text="Lorem ipsum dolor sit amet, qui.",
        location_id=kyiv_address.id,
    )

    session.add(kyiv_address)
    session.add(adding_shamestory)
    session.commit()

    result: ShameStory = session.get_one(ShameStory, 3)

    assert result.text == "Lorem ipsum dolor sit amet, qui."
    assert result.location == kyiv_address
    assert result.author.username == "tuki"


def test_db_get_shamestory_by_id(session: Session):
    id = 0
    shamestory_db = session.get(ShameStory, id)

    assert shamestory_db is not None
    assert (
        shamestory_db.text
        == "Lorem ipsum dolor sit amet, qui minim labore adipisicing minim sint cillum sint consectetur cupidatat."
    )
    assert shamestory_db.author_id == 0


def test_db_get_shamestories_by_location(session: Session):
    location = session.scalar(
        select(Address).where(
            Address.city == "Lviv", Address.street == "Hrinchenka, 14a"
        )
    )
    assert location is not None

    shamestories_db = (
        session.execute(
            select(ShameStory).where(ShameStory.location_id == location.id).limit(5)
        )
        .scalars()
        .all()
    )

    assert len(shamestories_db) <= 5

    example = shamestories_db[0]
    assert (
        example.text
        == "Lorem ipsum dolor sit amet, qui minim labore adipisicing minim sint cillum sint consectetur cupidatat."
    )
    assert example.author_id == 0


def test_db_agree_shamestory(session: Session):
    shamestory = session.get(ShameStory, 0)
    assert shamestory is not None

    agree_value = shamestory.agree

    session.execute(
        update(ShameStory).where(ShameStory.id == 0).values(agree=agree_value + 1)
    )
    session.commit()

    result = session.get_one(ShameStory, 0)
    assert result.agree == agree_value + 1


def test_db_disagree_shamestory(session: Session):
    shamestory = session.get(ShameStory, 0)
    assert shamestory is not None

    agree_value = shamestory.agree

    session.execute(
        update(ShameStory).where(ShameStory.id == 0).values(agree=agree_value - 1)
    )
    session.commit()

    result = session.get_one(ShameStory, 0)
    assert result.agree == agree_value - 1


def test_db_update_shamestory(session: Session):
    id: int = 0
    session.execute(
        update(ShameStory)
        .where(ShameStory.id == id)
        .values(
            author_id=32,
            text="Lorem ipsum dolor sit amet, qui.",
            location_id=3,
        )
    )
    session.commit()

    result: ShameStory = session.get_one(ShameStory, id)
    assert result is not None
    assert result.author_id == 32
    assert result.text == "Lorem ipsum dolor sit amet, qui."

    loc: Address = result.location
    assert loc is not None
    assert loc.city == "Ternopil"
    assert loc.street == "Ostrozkiy, 53"


def test_db_delete_shamestory(session: Session):
    id = 0
    session.execute(delete(ShameStory).where(ShameStory.id == id))
    result = session.get(ShameStory, id)
    assert result is None
