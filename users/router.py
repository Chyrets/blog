from fastapi import APIRouter, HTTPException, status
from pwdlib import PasswordHash
from sqlmodel import select

from .models import CreateUser, GetUser, User

from ..database import SessionDep


password_hash = PasswordHash.recommended()


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/{username}")
async def get_user(session: SessionDep, username: str) -> GetUser:
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    
    return user


@router.post("")
async def create_user(session: SessionDep, user: CreateUser):
    user_dict = user.model_dump()
    hashed_password = password_hash.hash(user_dict.get("password"))
    user_dict["hashed_password"] = hashed_password

    db_user = User.model_validate(User(**user_dict))
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    
    return db_user
