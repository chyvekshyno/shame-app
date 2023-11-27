from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config.settings import settings


engine = create_engine(settings.DATABASE_URL_PSYCOPG)
SessionLocal = sessionmaker(engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_database():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

