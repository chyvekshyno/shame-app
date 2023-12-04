from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..database import get_database
from . import (
    dependencies as deps,
    repository as user_repo,
    schemas,
)


router = APIRouter(tags=["Authentication"])


AuthForm = Annotated[OAuth2PasswordRequestForm, Depends()]
Database = Annotated[Session, Depends(get_database)]


@router.post("/signup", response_model=schemas.User)
def create_user(new_user: schemas.CreateUser, db: Database):
    if user_repo.contains(db=db, username=new_user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username already exist.",
        )
    user = user_repo.add(db=db, user=new_user)
    return user


@router.post("/login", response_model=schemas.Token)
def login_user(db: Database, form_data: AuthForm):
    user = user_repo.get_by_username(db=db, username=form_data.username)
    if not user or not user.validate_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password.",
        )
    return user.generate_access_token()


@router.get("/users/me", response_model=schemas.User)
def get_current_user(user: deps.CurrentActiveUser):
    return user


@router.get("/users/{username}", response_model=schemas.User)
def get_user(username: str, db: Database):
    return user_repo.get_by_username(db=db, username=username)
