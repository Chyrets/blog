from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select, or_

from app.users.models import User
from app.users.services import get_current_user, get_current_user_or_none
from .models import CreatePost, CreateTag, Post, PostWIthAuthor, Tag, UpdatePost
from ..database import SessionDep


router = APIRouter(
    prefix="/posts",
    tags=["posts"],
)


@router.get("/{post_id}")
async def get_post(session: SessionDep, post_id: int, current_user: Annotated[User, Depends(get_current_user_or_none)]) -> PostWIthAuthor:
    if current_user:
        stmt = (
            select(Post)
            .join(User)
            .where(Post.id == post_id, Post.deleted == False)
            .where(or_(User.is_private == False, User.id == current_user.id))
        )
    else:
        stmt = (
            select(Post)
            .join(User)
            .where(Post.id == post_id, Post.deleted == False)
            .where(User.is_private == False)
        )
    post = session.exec(stmt).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")
    
    return post


@router.get("/")
async def get_posts(
    session: SessionDep,
    current_user: Annotated[User | None, Depends(get_current_user_or_none)],
    offset: int = 0, 
    limit: int = Query(default=10, le=10)
) -> list[PostWIthAuthor]:
    if current_user:
        stmt = (
            select(Post)
            .join(User)
            .where(Post.deleted == False)
            .where(or_(User.is_private == False, User.id == current_user.id))
            .offset(offset)
            .limit(limit)
        )
    else:
        stmt = (
            select(Post)
            .join(User)
            .where(Post.deleted == False)
            .where(User.is_private == False)
            .offset(offset)
            .limit(limit)
        )
    posts = session.exec(stmt).all()

    return posts


@router.post("/")
async def create_post(session: SessionDep, post: CreatePost, current_user: Annotated[User, Depends(get_current_user)]) -> PostWIthAuthor:
    post_data = post.model_dump()

    post_data["author_id"] = current_user.id
    post_data["author"] = current_user

    tags = post_data.get("tags")
    tags_db = session.exec(select(Tag).where(Tag.title.in_(tags))).all()
    post_data["tags"] = tags_db

    db_post = Post.model_validate(Post(**post_data))
    
    session.add(db_post)
    session.commit()
    session.refresh(db_post)

    return db_post


@router.patch("/{post_id}")
async def update_post(session: SessionDep, post_id: int, post: UpdatePost, current_user: Annotated[User, Depends(get_current_user)]) -> PostWIthAuthor:
    post_db = session.get(Post, post_id)
    if not post_db:
        raise HTTPException(status_code=404, detail="Post not found.")
    if post_db.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden.")
    
    post_data = post.model_dump(exclude_unset=True)
    
    tags = post_data.get("tags")
    tags_db = session.exec(select(Tag).where(Tag.title.in_(tags))).all()
    post_db.tags.extend(tags_db)

    post_db.sqlmodel_update(post_data)
    session.add(post_db)
    session.commit()
    session.refresh(post_db)

    return post_db


@router.delete("/{post_id}")
async def delete_post(session: SessionDep, post_id: int, current_user: Annotated[User, Depends(get_current_user)]) -> dict:
    post_db = session.get(Post, post_id)
    if not post_db:
        raise HTTPException(status_code=404, detail="Post not found.")
    if post_db.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden.")
    
    post_db.deleted = True
    post_db.deleted_at = datetime.now(timezone.utc)
    session.commit()

    return {"message": f"Post with id={post_id} was successfully deleted."}


@router.post("/tags")
async def create_tag(session: SessionDep, tag: CreateTag, current_user: Annotated[User, Depends(get_current_user)]):
    db_tag = Tag.model_validate(tag)
    session.add(db_tag)
    session.commit()
    session.refresh(db_tag)

    return db_tag
