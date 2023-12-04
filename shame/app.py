from contextlib import asynccontextmanager

from fastapi import FastAPI

from . import models, route as shame_route
from .auth import route as auth_route
from .database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=engine)
    yield
    models.Base.metadata.drop_all(bind=engine)


app = FastAPI(lifespan=lifespan)

app.include_router(router=shame_route.router)
app.include_router(router=auth_route.router)


@app.get("/")
def root():
    return {"msg": "Hello Shame Application!"}
