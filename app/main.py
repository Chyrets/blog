from fastapi import FastAPI

from .database import create_db_and_tables
from .content.router import router as content_rounter
from .users.router import router as users_router

app = FastAPI()

app.include_router(content_rounter)
app.include_router(users_router)


# @app.on_event("startup")
# def on_startup():
#     create_db_and_tables()


@app.get("/")
async def root():
    return {"message": "Main page"}
