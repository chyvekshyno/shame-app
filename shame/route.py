from typing import Annotated

from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from . import schemas, repository as repo
from .database import get_database


router = APIRouter(prefix="/shamestories")

Database = Annotated[Session, Depends(get_database)]


@router.get("/", response_model=list[schemas.ShameStory])
def get_shamestories(db: Database, skip: int = 0, limit: int = 20):
    results = repo.fetch(db, skip=skip, limit=limit)
    return results


@router.get("/{shamestory_id}", response_model=schemas.ShameStory)
def get_shamestory_by_id(shamestory_id: int, db: Database):
    result = repo.fetch_by_id(session=db, shamestory_id=shamestory_id)
    return result


@router.post("/", response_model=schemas.ShameStory)
def insert_shamestory(shamestory: schemas.CreateShameStory, db: Database):
    db_shamestory = repo.add(session=db, shamestory=shamestory)
    return db_shamestory


@router.put("/{shamestory_id}", response_model=schemas.ShameStory)
def update_shamestory(
    shamestory_id: int,
    shamestory_values: schemas.CreateShameStory,
    db: Database,
):
    db_shamestory = repo.update(
        session=db,
        shamestory_id=shamestory_id,
        values=shamestory_values,
    )
    return db_shamestory


@router.delete("/{shamestory_id}")
def delete_shamestory(shamestory_id: int, db: Database):
    repo.delete(session=db, shamestory_id=shamestory_id)
