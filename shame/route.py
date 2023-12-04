from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from shame.auth import dependencies

from . import schemas, repository as repo
from .database import get_database


router = APIRouter(prefix="/shamestories")

Database = Annotated[Session, Depends(get_database)]


@router.get("/", response_model=list[schemas.ShameStory])
def get_shamestories(db: Database, skip: int = 0, limit: int = 20):
    results = repo.get(db, skip=skip, limit=limit)
    return results


@router.get("/{shamestory_id}", response_model=schemas.ShameStory)
def get_shamestory_by_id(shamestory_id: int, db: Database):
    try:
        result = repo.get_by_id(db=db, shamestory_id=shamestory_id)
        return result
    except NoResultFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/", response_model=schemas.ShameStory)
def insert_shamestory(
    shamestory: schemas.CreateShameStory,
    address: schemas.CreateAddress,
    user: dependencies.CurrentActiveUser,
    db: Database,
):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="To post ShameStory user should be authorized.",
        )

    try:
        db_address = repo.get_address(db=db, address=address)
    except NoResultFound:
        db_address = repo.add_address(db=db, address=address)

    db_shamestory = repo.add(
        db=db,
        shamestory=shamestory,
        author_id=user.id,
        address_id=db_address.id,
    )
    return db_shamestory


@router.put("/{shamestory_id}", response_model=schemas.ShameStory)
def update_shamestory(
    shamestory_id: int,
    shamestory_values: schemas.CreateShameStory,
    user: dependencies.CurrentActiveUser,
    db: Database,
):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="To update ShameStory user should be authorized.",
        )

    db_shamestory = repo.update(
        db=db,
        shamestory_id=shamestory_id,
        values=shamestory_values,
    )
    return db_shamestory


@router.delete("/{shamestory_id}")
def delete_shamestory(
    shamestory_id: int,
    user: dependencies.CurrentActiveUser,
    db: Database,
):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="To delete ShameStory user should be authorized.",
        )

    repo.delete(db=db, shamestory_id=shamestory_id)
