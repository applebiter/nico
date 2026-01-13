"""Database connection and session management."""
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from nico.domain.models.base import Base


class DatabaseConfig:
    """Database configuration and connection management."""
    
    def __init__(self, database_url: str) -> None:
        """Initialize database connection.
        
        Args:
            database_url: PostgreSQL connection string
                Format: postgresql://user:password@host:port/database
        """
        self.database_url = database_url
        self.engine = create_engine(
            database_url,
            echo=False,  # Set to True for SQL query logging
            pool_pre_ping=True,  # Verify connections before using
            pool_size=5,
            max_overflow=10,
        )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
        )
    
    def create_tables(self) -> None:
        """Create all tables defined in models.
        
        Note: In production, use Alembic migrations instead.
        This is useful for development and testing.
        """
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self) -> None:
        """Drop all tables.
        
        Warning: This will delete all data! Use with caution.
        """
        Base.metadata.drop_all(bind=self.engine)
    
    def get_session(self) -> Generator[Session, None, None]:
        """Get a database session.
        
        Yields:
            SQLAlchemy session
            
        Example:
            >>> db = DatabaseConfig("postgresql://...")
            >>> with db.get_session() as session:
            ...     project = session.query(Project).first()
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


# Global database instance (initialized by application)
_db_instance: DatabaseConfig | None = None


def init_db(database_url: str) -> DatabaseConfig:
    """Initialize the global database instance.
    
    Args:
        database_url: PostgreSQL connection string
        
    Returns:
        DatabaseConfig instance
    """
    global _db_instance
    _db_instance = DatabaseConfig(database_url)
    return _db_instance


def get_db() -> DatabaseConfig:
    """Get the global database instance.
    
    Returns:
        DatabaseConfig instance
        
    Raises:
        RuntimeError: If database not initialized
    """
    if _db_instance is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _db_instance
