from pydantic import BaseModel
from pydantic.config import ConfigDict


class ShameStoryBase(BaseModel):
    title: str
    text: str


class ShameStory(ShameStoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    agree: int = 0
    author_id: int
    address_id: int | None = None


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
