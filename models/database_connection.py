"""
SENTINEL Database Connection
Database session management and connection utilities
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import logging
from typing import Generator

from config.settings import settings
from models.database import Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database connection and session management"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize database engine with connection pooling"""
        try:
            # Use StaticPool only for SQLite, otherwise use default pool
            if settings.DATABASE_URL.startswith("sqlite"):
                self.engine = create_engine(
                    settings.DATABASE_URL,
                    connect_args={"check_same_thread": False},
                    poolclass=StaticPool,
                    echo=settings.DEBUG
                )
            else:
                self.engine = create_engine(
                    settings.DATABASE_URL,
                    pool_pre_ping=True,
                    pool_recycle=3600,
                    echo=settings.DEBUG
                )
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            logger.info("Database engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")
            raise
    
    def create_tables(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise
    
    def drop_tables(self):
        """Drop all database tables (use with caution)"""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.info("Database tables dropped successfully")
        except Exception as e:
            logger.error(f"Failed to drop database tables: {e}")
            raise
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Context manager for database sessions"""
        if self.SessionLocal is None:
            raise RuntimeError("Database session factory is not initialized.")
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def get_session_direct(self) -> Session:
        """Get a database session directly (manual management required)"""
        if self.SessionLocal is None:
            raise RuntimeError("Database session factory is not initialized.")
        return self.SessionLocal()
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False

# Global database manager instance
db_manager = DatabaseManager()

# Dependency for FastAPI
def get_db() -> Generator[Session, None, None]:
    """Dependency function for FastAPI to get database session"""
    with db_manager.get_session() as session:
        yield session 