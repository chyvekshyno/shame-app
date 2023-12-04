from datetime import timedelta
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from . import utils

if TYPE_CHECKING:
    from ..models import ShameStory
else:
    ShameStory = "ShameStory"


class User(Base):
    __tablename__ = "Users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[Optional[str]]
    full_name: Mapped[Optional[str]]
    username: Mapped[str]
    password_hashed: Mapped[str]
    rating: Mapped[int] = mapped_column(default=0)
    stories: Mapped[List[ShameStory]] = relationship(
        "ShameStory", back_populates="author"
    )

    @staticmethod
    def hash_password(password: str) -> str:
        return utils.hash_password(password)

    def validate_password(self, password: str) -> bool:
        return utils.verify_password(password, self.password_hashed)

    def generate_access_token(self, expires_delta: timedelta | None = None):
        return {
            "access_token": utils.create_access_token(
                subject=self.username,
                expires_delta=expires_delta,
            ),
            "token_type": "bearer",
        }

    def __repr__(self) -> str:
        return (
            f"User(id={self.id!r}"
            f", email={self.email!r}"
            f", username={self.username!r}"
            f", full_name={self.full_name!r}"
            f", rating={self.rating!r})"
        )
