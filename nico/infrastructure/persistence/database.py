"""Database connection and session management."""

from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .models import Base


class Database:
    """Database connection manager."""

    def __init__(self, db_path: Path, echo: bool = False):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
            echo: Whether to log SQL statements
        """
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}", echo=echo)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def create_tables(self) -> None:
        """Create all tables in the database."""
        Base.metadata.create_all(bind=self.engine)

    def get_session(self) -> Generator[Session, None, None]:
        """Get a database session."""
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()
