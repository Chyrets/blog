from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from sqlalchemy.orm import contains_eager

from app.content.models import Post

from .models import CreateUser, GetUser, GetUserWithPosts, User, Token
from .services import authenticate_user, create_access_token, get_current_user
from .config import ACCESS_TOKEN_EXPIRE_MINUTES, password_hash

from ..database import SessionDep


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/token")
async def login_for_access_token(session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expire
    )

    return Token(access_token=access_token, token_type="Bearer")


@router.get("/me")
async def read_current_user(current_user: Annotated[User, Depends(get_current_user)]) -> GetUser:
    return current_user


@router.get("/{username}")
async def get_user_by_username(session: SessionDep, username: str) -> GetUserWithPosts:
    statement = (
        select(User)
        .where(User.username==username)
        .join(User.posts)
        .filter(Post.deleted==False)
        .options(contains_eager(User.posts))
        )
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        
    return user


@router.post("")
async def create_user(session: SessionDep, user: CreateUser) -> GetUser:
    user_dict = user.model_dump()
    hashed_password = password_hash.hash(user_dict.get("password"))
    user_dict["hashed_password"] = hashed_password

    db_user = User.model_validate(User(**user_dict))
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    
    return db_user


@router.post("/change_status")
async def change_user_status(session: SessionDep, current_user: Annotated[User, Depends(get_current_user)]) -> dict:
    current_user.is_private = not current_user.is_private
    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return {"message": f"Current user has successfully changed their status to {"private" if current_user.is_private else "public"}"}
