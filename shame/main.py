from contextlib import asynccontextmanager

from fastapi import FastAPI

from . import models
from .database import engine
from .route import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=engine)
    yield
    models.Base.metadata.drop_all(bind=engine)


app = FastAPI(lifespan=lifespan)

app.include_router(router)


@app.get("/")
def root():
    return {"msg": "Hello Shame Application!"}
