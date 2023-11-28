from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    email: str


class CreateUser(UserBase):
    password: str


class User(UserBase):
    id: int


class ShameStoryBase(BaseModel):
    text: str
    agree: int = 0
    author_id: int
    location_id: int | None = None


class ShameStory(ShameStoryBase):
    id: int


class UpdateShameStory(ShameStoryBase):
    pass


class CreateShameStory(ShameStoryBase):
    pass


class AddressBase(BaseModel):
    country: str
    state: str
    city: str
    street: str


class Address(AddressBase):
    id: int


class CreateAddress(AddressBase):
    pass
