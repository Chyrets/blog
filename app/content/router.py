from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select

from app.users.models import User
from app.users.services import get_current_user

from .models import CreatePost, Post, PostWIthAuthor, UpdatePost
from ..database import SessionDep


router = APIRouter(
    prefix="/posts",
    tags=["posts"],
)


@router.get("/")
async def get_posts(session: SessionDep, offset: int = 0, limit: int = Query(default=10, le=10)) -> list[PostWIthAuthor]:
    posts = session.exec(select(Post).offset(offset).limit(limit)).all()

    return posts


@router.get("{post_id}")
async def get_post(session: SessionDep, post_id: int) -> PostWIthAuthor:
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")
    
    return post


@router.post("/")
async def create_post(session: SessionDep, post: CreatePost, current_user: Annotated[User, Depends(get_current_user)]) -> Post:
    post_dict = post.model_dump()
    post_dict["author_id"] = current_user.id
    post_dict["author"] = current_user
    db_post = Post.model_validate(Post(**post_dict))
    session.add(db_post)
    session.commit()
    session.refresh(db_post)

    return db_post


@router.patch("{post_id}")
async def update_post(session: SessionDep, post_id: int, post: UpdatePost, current_user: Annotated[User, Depends(get_current_user)]) -> Post:
    post_db = session.get(Post, post_id)
    if not post_db:
        raise HTTPException(status_code=404, detail="Post not found.")
    if post_db.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden.")
    
    post_data = post.model_dump(exclude_unset=True)
    post_db.sqlmodel_update(post_data)
    session.add(post_db)
    session.commit()
    session.refresh(post_db)

    return post_db


@router.delete("{post_id}")
async def delete_post(session: SessionDep, post_id: int, current_user: Annotated[User, Depends(get_current_user)]) -> dict:
    post_db = session.get(Post, post_id)
    if not post_db:
        raise HTTPException(status_code=404, detail="Post not found.")
    if post_db.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden.")
    
    session.delete(post_db)
    session.commit()

    return {"message": f"Post with id={post_id} was successfully deleted."}
