"""
Database setup.

We use SQLite, a database that lives in a single file (urls.db) with zero
configuration — perfect for small projects. SQLModel is a thin, modern layer
on top of SQLAlchemy that lets us define tables as regular Python classes.
"""

from sqlmodel import SQLModel, create_engine, Session

# The database is just a file next to the code.
DATABASE_URL = "sqlite:///urls.db"

# check_same_thread=False is required for SQLite to work with FastAPI,
# which may access the database from different threads.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def init_db() -> None:
    """Create the database tables if they don't exist yet."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Yield a database session (used by FastAPI dependency injection)."""
    with Session(engine) as session:
        yield session
