from sqlmodel import Field, SQLModel


class Post(SQLModel, table=True):
    id: int | None = Field
    title: str = Field(index=True)
    content: str = Field()
    category: str | None = Field(default=None)
    tags: list[str] | None = Field(default=None)
    