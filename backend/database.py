"""
Database connection setup.

Uses SQLite by default so you can run this with zero extra installs.
When you're ready for production (or want pgvector for semantic search
later), just set the DATABASE_URL environment variable to a Postgres
connection string — nothing else in this project needs to change.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./local_bites.db")

# Some hosts (Railway, Heroku) hand out URLs starting with "postgres://",
# but SQLAlchemy needs "postgresql://" — patch it automatically so this
# doesn't turn into a confusing error later.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency that provides a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
