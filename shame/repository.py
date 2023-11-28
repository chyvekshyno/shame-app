from typing import Sequence
from sqlalchemy import delete, select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from . import models
from . import schemas


class ShameStoryRepository:
    def add(
        self,
        session: Session,
        shamestory: schemas.CreateShameStory,
    ) -> models.ShameStory:
        new_db_shamestory = models.ShameStory(**shamestory.model_dump())
        session.add(new_db_shamestory)
        session.commit()
        return new_db_shamestory

    #
    def add_location(
        self,
        session: Session,
        address: schemas.CreateAddress,
    ) -> models.Address:
        found = session.scalar(
            select(models.Address).where(
                (models.Address.country == address.country)
                & (models.Address.state == address.state)
                & (models.Address.city == address.city)
                & (models.Address.street == address.street)
            )
        )
        if found:
            return found

        db_address = models.Address(**address.model_dump())
        session.add(db_address)
        session.commit()
        return db_address

    #
    def fetch(
        self,
        session: Session,
        skip: int,
        limit: int,
    ) -> Sequence[models.ShameStory]:
        result = (
            session.execute(
                select(models.ShameStory)
                .offset(skip)
                .limit(limit)
                .order_by(models.ShameStory.agree)
            )
            .scalars()
            .all()
        )

        return result

    #
    def fetch_by_id(self, session: Session, shamestory_id: int) -> models.ShameStory:
        result = session.get(models.ShameStory, shamestory_id)
        if not result:
            raise NoResultFound
        return result

    #
    def fetch_by_location(
        self,
        session: Session,
        location_id: int,
        skip: int = 0,
        limit: int = 50,
    ) -> Sequence[models.ShameStory]:
        try:
            result = session.scalars(
                select(models.ShameStory)
                .where(models.ShameStory.location_id == location_id)
                .offset(skip)
                .limit(limit)
            ).all()
            return result
        except NoResultFound:
            return []

    #
    def fetch_by_author(
        self,
        session: Session,
        author_id: int,
        skip: int = 0,
        limit: int = 50,
    ) -> Sequence[models.ShameStory]:
        try:
            result = session.scalars(
                select(models.ShameStory)
                .where(models.ShameStory.author_id == author_id)
                .offset(skip)
                .limit(limit)
            ).all()
            return result
        except Exception:
            return []

    #
    def fetch_user(self, session: Session, user_id: int) -> models.User:
        result = session.get(models.User, user_id)
        if not result:
            raise NoResultFound("")
        return result

    #
    def update(
        self,
        session: Session,
        values: schemas.ShameStory,
    ) -> models.ShameStory | None:
        try:
            updated = session.scalar(
                update(models.ShameStory)
                .where(models.ShameStory.id == values.id)
                .values(**values.model_dump())
                .returning(models.ShameStory)
            )
            session.commit()
            return updated
        except Exception:
            raise Exception("Exception at Updating")

    #
    def delete(self, session: Session, shamestory_id: int) -> None:
        try:
            session.execute(
                delete(models.ShameStory).where(models.ShameStory.id == shamestory_id)
            )
            session.commit()
        except Exception:
            raise Exception("None to DELETE")
