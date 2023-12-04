from typing import Sequence

import sqlalchemy
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from shame.auth import utils

from . import models, schemas


def contains(db: Session, username: str) -> bool:
    result = db.execute(
        sqlalchemy.select(models.User).where(models.User.username == username)
    ).scalar_one_or_none()
    return result is not None


def get(db: Session, skip: int = 0, limit: int = 10) -> Sequence[models.User]:
    result = (
        db.execute(
            sqlalchemy.select(models.User)
            .offset(skip)
            .limit(limit)
            .order_by(models.User.rating)
        )
        .scalars()
        .all()
    )

    return result


def get_by_username(db: Session, username: str) -> models.User:
    result = db.execute(
        sqlalchemy.select(models.User).where(models.User.username == username)
    ).scalar()

    if not result:
        raise NoResultFound(f"Could not find user with :username={username}")
    return result


def get_by_email(db: Session, email: str) -> models.User:
    result = db.execute(
        sqlalchemy.select(models.User).where(models.User.email == email)
    ).scalar()

    if not result:
        raise NoResultFound(f"Could not find user with :email={email}")
    return result


def get_by_id(db: Session, id: int) -> models.User:
    result = db.get(models.User, id)
    if not result:
        raise NoResultFound(f"Could not find user with :id={id}")
    return result


def add(db: Session, user: schemas.CreateUser) -> models.User:
    db_user = models.User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        password_hashed=utils.hash_password(user.password),
    )
    db.add(db_user)
    db.commit()
    return db_user


def update(db: Session, id: int, values: schemas.UserBase) -> models.User:
    if not db.get(models.User, id):
        raise NoResultFound(f"Could not find user with :id={id}")

    db.execute(
        sqlalchemy.update(models.User)
        .where(models.User.id == id)
        .values(**values.model_dump(exclude_unset=True))
    )
    updated_db_user = get_by_id(db=db, id=id)
    return updated_db_user


def delete(db: Session, id: int):
    try:
        db.execute(sqlalchemy.delete(models.User).where(models.User.id == id))
        db.commit()
    except Exception as e:
        raise e
