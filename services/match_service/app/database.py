from functools import lru_cache

from pydantic import ValidationError
from sqlalchemy import URL, create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from .config import get_settings


@lru_cache
def get_engine() -> Engine:
    settings = get_settings()

    database_url = URL.create(
        drivername="postgresql+psycopg",
        username=settings.db_user,
        password=settings.db_password.get_secret_value(),
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
    )

    return create_engine(
        database_url,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 3},
    )


def database_is_available() -> bool:
    try:
        with get_engine().connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return result.scalar_one() == 1

    except (SQLAlchemyError, ValidationError):
        return False