import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .settings import config

# Note: The settings.py config dictionary uses 'dev', 'prod', 'test' keys.
# Defaulting to 'dev' instead of 'development'.
env = os.environ.get("FLASK_CONFIG", "dev")
settings = config.get(env, config["dev"])

if not settings.SQLALCHEMY_DATABASE_URI:
    # Fallback for dev if env var is missing
    db_uri = "sqlite:///" + os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "db.sqlite"
    )
else:
    db_uri = settings.SQLALCHEMY_DATABASE_URI

engine = create_engine(db_uri, connect_args={"check_same_thread": False})
session_maker = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_session() -> Generator[Session, None, None]:
    with session_maker() as session:
        yield session
