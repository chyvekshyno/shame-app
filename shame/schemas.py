from pydantic import BaseModel
from pydantic.config import ConfigDict


class UserBase(BaseModel):
    username: str
    email: str


class CreateUser(UserBase):
    password: str


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class ShameStoryBase(BaseModel):
    text: str
    agree: int = 0
    author_id: int
    location_id: int | None = None


class ShameStory(ShameStoryBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class CreateShameStory(ShameStoryBase):
    pass


class AddressBase(BaseModel):
    country: str
    state: str
    city: str
    street: str


class Address(AddressBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class CreateAddress(AddressBase):
    pass
