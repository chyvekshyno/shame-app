from typing import Annotated

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from . import schemas, repository as user_repo
from ..database import SessionLocal
from ..config.auth import auth_settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login", scheme_name="JWT")


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token=token,
            key=auth_settings.JWT_SECRET_KEY,
            algorithms=[auth_settings.ALGORITHM],
        )
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = user_repo.get_by_username(db=SessionLocal(), username=username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not find user with username:{user.username}",
        )
    return user


CurrentUser = Annotated[schemas.User, Depends(get_current_user)]


def get_current_active_user(current_user: CurrentUser):
    # if not current_user.active:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


CurrentActiveUser = Annotated[schemas.User, Depends(get_current_active_user)]
