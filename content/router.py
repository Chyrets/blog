from fastapi import APIRouter, HTTPException
from sqlmodel import select

from .models import CreatePost, Post, UpdatePost
from ..database import SessionDep


router = APIRouter(
    prefix="/posts",
    tags=["posts"],
)


@router.get("/")
async def get_posts(session: SessionDep) -> list[Post]:
    posts = session.exec(select(Post)).all()

    return posts


@router.get("{post_id}")
async def get_post(session: SessionDep, post_id: int) -> Post:
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")
    
    return post


@router.post("/")
async def create_post(session: SessionDep, post: CreatePost) -> Post:
    db_post = Post.model_validate(post)
    session.add(db_post)
    session.commit()
    session.refresh(db_post)

    return db_post


@router.patch("{post_id}")
async def update_post(session: SessionDep, post_id: int, post: UpdatePost) -> Post:
    post_db = session.get(Post, post_id)
    if not post_db:
        raise HTTPException(status_code=404, detail="Post not found.")
    post_data = post.model_dump(exclude_unset=True)
    post_db.sqlmodel_update(post_data)
    session.add(post_db)
    session.commit()
    session.refresh(post_db)

    return post_db
