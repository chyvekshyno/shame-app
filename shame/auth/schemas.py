from pydantic import BaseModel
from pydantic.config import ConfigDict


##########################
#         Users          #
##########################


class UserBase(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class UserInDB(User):
    password_hashed: str


class CreateUser(UserBase):
    password: str


##########################
#         Tokens         #
##########################


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class TokenPayload(BaseModel):
    sub: str | None = None
    exp: int | None = None
