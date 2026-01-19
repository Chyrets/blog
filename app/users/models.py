from typing import TYPE_CHECKING

from pydantic import BaseModel
from sqlalchemy.sql import false
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.content.models import Post


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class BaseUser(SQLModel):
    username: str = Field(index=True)


class User(BaseUser, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str = Field()
    # is_admin: bool = Field(default=False)
    posts: list["Post"] = Relationship(back_populates="author")
    is_private: bool = Field(default=False, sa_column_kwargs={"server_default": false()})


class GetUser(BaseUser):
    id: int
    is_private: bool


class GetPrivateUser(GetUser):
    pass


class GetUserWithPosts(GetUser):
    posts: list


class CreateUser(BaseUser):
    password: str = Field()


class UpdateUser(BaseUser):
    pass


class UserPublic(BaseUser):
    id: int
