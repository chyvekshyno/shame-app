from datetime import datetime, timedelta
from typing import Any

from jose import jwt

from . import schemas
from ..config.auth import auth_settings


def get_fake_user(token: str):
    return schemas.User(
        id=0,
        username=token + "tuki",
        email="tuky.shyvekshyno@gmail.com",
        full_name="Artur Onyshkevych",
    )


def hash_password(password: str) -> str:
    return auth_settings.PASSWORD_CONTEXT.hash(password)


def verify_password(password: str, password_hashed: str) -> bool:
    return auth_settings.PASSWORD_CONTEXT.verify(
        secret=password,
        hash=password_hashed,
    )


def _create_token(
    subject: str | Any,
    minutes_to_expires: int,
    secret_key: str,
    algorithm: str,
    expires_delta: timedelta | None = None,
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode,
        key=auth_settings.JWT_SECRET_KEY,
        algorithm=auth_settings.ALGORITHM,
    )
    return encoded_jwt


def create_access_token(
    subject: str | Any,
    expires_delta: timedelta | None = None,
) -> str:
    return _create_token(
        subject=subject,
        minutes_to_expires=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        secret_key=auth_settings.JWT_SECRET_KEY,
        algorithm=auth_settings.ALGORITHM,
        expires_delta=expires_delta,
    )


def create_refresh_token(
    subject: str | Any,
    expires_delta: timedelta | None = None,
) -> str:
    return _create_token(
        subject=subject,
        minutes_to_expires=auth_settings.REFRESH_TOKEN_EXPIRE_MINUTES,
        secret_key=auth_settings.JWT_REFRESH_SECRET_KEY,
        algorithm=auth_settings.ALGORITHM,
        expires_delta=expires_delta,
    )
