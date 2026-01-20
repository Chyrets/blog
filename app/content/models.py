from datetime import datetime
from sqlmodel import DateTime, Field, Relationship, SQLModel, Column, func

from app.users.models import User, UserPublic


class PostTagLink(SQLModel, table=True):
    post_id: int | None = Field(default=None, foreign_key="post.id", primary_key=True)
    tag_id: int | None = Field(default=None, foreign_key="tag.id", primary_key=True)


class BasePost(SQLModel):
    title: str = Field(index=True)
    content: str = Field()
    category: str | None = Field(default=None)


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

    tags: list["Tag"] = Relationship(back_populates="posts", link_model=PostTagLink)


class PostPublic(BasePost):
    id: int


class CreatePost(BasePost):
    tags: list[str] | None = None


class UpdatePost(BasePost):
    title: str | None = None
    content: str | None = None
    category: str | None = None
    tags: list[str] | None = None


class PostWIthAuthor(BasePost):
    id: int
    author: UserPublic
    tags: list["Tag"] 


class BaseTag(SQLModel):
    title: str = Field(index=True)


class Tag(BaseTag, table=True):
    id: int | None = Field(default=None, primary_key=True)

    posts: list[Post] = Relationship(back_populates="tags", link_model=PostTagLink)


class CreateTag(BaseTag):
    pass
    