from pydantic_settings import BaseSettings, SettingsConfigDict
from passlib.context import CryptContext


class AuthSettings(BaseSettings):
    ALGORITHM: str
    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int

    @property
    def PASSWORD_CONTEXT(self) -> CryptContext:
        return CryptContext(schemes=["bcrypt"], deprecated="auto")

    model_config = SettingsConfigDict(env_file=".env_auth")


auth_settings = AuthSettings()  # pyright: ignore
