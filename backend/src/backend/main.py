from fastapi import FastAPI

from .routers import categories, users

app = FastAPI()

app.include_router(users.router)
app.include_router(categories.router)
