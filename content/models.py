from sqlmodel import Field, SQLModel


class BasePost(SQLModel):
    title: str = Field(index=True)
    content: str = Field()
    category: str | None = Field(default=None)
    tags: list[str] | None = Field(default=None)


class Post(BasePost, table=True):
    id: int | None = Field


class CreatePost(BasePost):
    pass


class UpdatePost(BasePost):
    title: str | None = None
    content: str | None = None
    category: str | None = None
    tags: list[str] | None = None
    