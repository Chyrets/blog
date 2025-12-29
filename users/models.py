from sqlmodel import Field, SQLModel


class BaseUser(SQLModel):
    username: str = Field(index=True)


class User(BaseUser, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hassed_password: str = Field()
    # is_admin: bool = Field(default=False)


class CreateUser(BaseUser):
    password: str = Field()


class UpdateUser(BaseUser):
    pass
