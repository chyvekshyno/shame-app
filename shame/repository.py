from typing import Sequence
import sqlalchemy
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from . import models
from . import schemas


def add(
    db: Session,
    shamestory: schemas.CreateShameStory,
    author_id: int,
    address_id: int,
) -> models.ShameStory:
    new_db_shamestory = models.ShameStory(
        **shamestory.model_dump(),
        author_id=author_id,
        address_id=address_id,
    )
    db.add(new_db_shamestory)
    db.commit()
    return new_db_shamestory


def get_address(db: Session, address: schemas.CreateAddress) -> models.Address:
    result = db.scalar(
        sqlalchemy.select(models.Address).where(
            (models.Address.country == address.country)
            & (models.Address.state == address.state)
            & (models.Address.city == address.city)
            & (models.Address.street == address.street)
        )
    )
    if not result:
        raise NoResultFound(
            "No address in database with params ["
            f"country={address.country}, "
            f"state={address.state}, "
            f"city={address.city}, "
            f"street={address.street}]"
        )
    return result


def add_address(db: Session, address: schemas.CreateAddress) -> models.Address:
    db_address = models.Address(**address.model_dump())
    db.add(db_address)
    db.commit()
    return db_address


def get(db: Session, skip: int = 0, limit: int = 50) -> Sequence[models.ShameStory]:
    result = (
        db.execute(
            sqlalchemy.select(models.ShameStory)
            .offset(skip)
            .limit(limit)
            .order_by(models.ShameStory.agree)
        )
        .scalars()
        .all()
    )

    return result


def get_by_id(db: Session, shamestory_id: int) -> models.ShameStory:
    result = db.get(models.ShameStory, shamestory_id)
    if not result:
        raise NoResultFound(f"Could not find shamestory with :id={shamestory_id}")
    return result


def get_by_address(
    db: Session,
    address_id: int,
    skip: int = 0,
    limit: int = 50,
) -> Sequence[models.ShameStory]:
    result = db.scalars(
        sqlalchemy.select(models.ShameStory)
        .where(models.ShameStory.address_id == address_id)
        .offset(skip)
        .limit(limit)
    ).all()
    return result


def get_by_author(
    db: Session,
    author_id: int,
    skip: int = 0,
    limit: int = 50,
) -> Sequence[models.ShameStory]:
    result = db.scalars(
        sqlalchemy.select(models.ShameStory)
        .where(models.ShameStory.author_id == author_id)
        .offset(skip)
        .limit(limit)
    ).all()
    return result


def update(
    db: Session,
    shamestory_id: int,
    values: schemas.CreateShameStory,
) -> models.ShameStory | None:
    try:
        updated = db.scalar(
            sqlalchemy.update(models.ShameStory)
            .where(models.ShameStory.id == shamestory_id)
            .values(**values.model_dump(exclude_unset=True))
            .returning(models.ShameStory)
        )
        db.commit()
        return updated
    except Exception as e:
        raise e


def delete(db: Session, shamestory_id: int) -> None:
    try:
        db.execute(
            sqlalchemy.delete(models.ShameStory).where(
                models.ShameStory.id == shamestory_id
            )
        )
        db.commit()
    except Exception:
        raise Exception("None to DELETE")
