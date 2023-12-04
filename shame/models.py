from typing import List, TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

if TYPE_CHECKING:
    from .auth.models import User
else:
    User = "User"


class Address(Base):
    __tablename__ = "Addresses"

    id: Mapped[int] = mapped_column(primary_key=True)
    country: Mapped[str] = mapped_column()
    state: Mapped[str] = mapped_column()
    city: Mapped[str] = mapped_column()
    street: Mapped[str] = mapped_column()
    shamestories: Mapped[List["ShameStory"]] = relationship(
        # secondary=address_shamestory_association_table,
        back_populates="address",
    )

    def __repr__(self) -> str:
        return (
            f"Address(id={self.id!r}"
            f", country={self.country!r}"
            f", state={self.state!r}"
            f", city={self.city!r}"
            f", street={self.street!r})"
        )


class ShameStory(Base):
    """Describes bad experiences of users with linking to location where it happenned"""

    __tablename__ = "ShameStories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(50))
    text: Mapped[str]
    agree: Mapped[int] = mapped_column(default=0)

    address_id: Mapped[int] = mapped_column(ForeignKey("Addresses.id"))
    address: Mapped["Address"] = relationship(
        # secondary=address_shamestory_association_table,
        back_populates="shamestories",
    )

    author_id: Mapped[int] = mapped_column(ForeignKey("Users.id"))
    author: Mapped[User] = relationship(
        "User", back_populates="stories", foreign_keys=author_id
    )

    def __repr__(self) -> str:
        return (
            f"ShameStory(id={self.id!r}"
            f", text={self.text!r}"
            f", author={self.author!r}"
            f", address={self.address!r})"
        )
