from fastapi import APIRouter
from sqlmodel import select

from .models import Post
from ..database import SessionDep


router = APIRouter(
    prefix="/posts",
    tags=["posts"],
)


@router.get("/")
async def get_posts(session: SessionDep) -> list[Post]:
    posts = session.exec(select(Post)).all()

    return posts

