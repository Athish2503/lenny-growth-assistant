from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.database.base import Base

# Configure engine connect args and create engine with SQLite fallback on failure
def create_db_engine():
    db_url = settings.DATABASE_URL
    connect_args = {}
    if db_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    try:
        eng = create_engine(
            db_url,
            connect_args=connect_args,
            pool_pre_ping=True,
            echo=False
        )
        # Fast connection test
        with eng.connect() as conn:
            pass
        return eng, db_url
    except Exception as e:
        print(f"Database connection to {db_url} failed: {e}")
        print("Gracefully falling back to local SQLite database: sqlite:///./lenny_growth.db")
        sqlite_url = "sqlite:///./lenny_growth.db"
        sqlite_args = {"check_same_thread": False}
        eng = create_engine(
            sqlite_url,
            connect_args=sqlite_args,
            pool_pre_ping=True,
            echo=False
        )
        return eng, sqlite_url

engine, actual_db_url = create_db_engine()

# Enable foreign key support for SQLite connections
if actual_db_url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency function that yields a transactional database session per request
    and ensures proper closing on completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Helper function to initialize database tables directly (useful for testing and development).
    """
    Base.metadata.create_all(bind=engine)
