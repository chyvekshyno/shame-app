from typing import List

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = "Users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str]
    username: Mapped[str]
    password: Mapped[str]
    stories: Mapped[List["ShameStory"]] = relationship(back_populates="author")
    rating: Mapped[int] = mapped_column(default=0)

    def __repr__(self) -> str:
        return (
            f"User(id={self.id!r}"
            f", username={self.username!r}"
            f", rating={self.rating!r})"
        )


class Address(Base):
    __tablename__ = "Addresses"

    id: Mapped[int] = mapped_column(primary_key=True)
    country: Mapped[str] = mapped_column()
    state: Mapped[str] = mapped_column()
    city: Mapped[str] = mapped_column()
    street: Mapped[str] = mapped_column()
    shamestories: Mapped[List["ShameStory"]] = relationship(back_populates="location")

    def __repr__(self) -> str:
        return (
            f"Address(id={self.id!r}"
            f", country={self.country!r}"
            f", state={self.state!r}"
            f", city={self.city!r}"
            f", st.={self.street!r})"
        )


class ShameStory(Base):
    """Describes bad experiences of users with linking to location where it happenned"""

    __tablename__ = "ShameStories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    text: Mapped[str]
    agree: Mapped[int] = mapped_column(default=0)

    location_id: Mapped[int] = mapped_column(ForeignKey("Addresses.id"))
    location: Mapped["Address"] = relationship(back_populates="shamestories")

    author_id: Mapped[int] = mapped_column(ForeignKey("Users.id"))
    author: Mapped["User"] = relationship(back_populates="stories")

    def __repr__(self) -> str:
        return (
            f"ShameStory(id={self.id!r}"
            f", text={self.text!r}"
            f", author={self.author!r}"
            f", location={self.location!r})"
        )
