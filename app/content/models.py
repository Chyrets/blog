from datetime import datetime
from sqlmodel import DateTime, Field, Relationship, SQLModel, Column, func

from app.users.models import User, UserPublic


class BasePost(SQLModel):
    title: str = Field(index=True)
    content: str = Field()
    category: str | None = Field(default=None)
    # tags: list[str] | None = Field(default=None)


class Post(BasePost, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime | None = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), nullable=True
        )
    )
    updated: bool = Field(default=False)
    updated_at: datetime | None = Field(
        sa_column=Column(
            DateTime(timezone=True), onupdate=func.now(), nullable=True
        )
    )
    deleted: bool = Field(default=False)
    deleted_at: datetime | None = Field(default=None)
    
    author_id: int = Field(foreign_key="user.id")
    author: User = Relationship(back_populates="posts")


class PostPublic(BasePost):
    id: int


class CreatePost(BasePost):
    pass


class UpdatePost(BasePost):
    title: str | None = None
    content: str | None = None
    category: str | None = None
    # tags: list[str] | None = None


class PostWIthAuthor(BasePost):
    id: int
    author: UserPublic
    