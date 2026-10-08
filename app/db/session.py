from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# The engine handles the physical connection pool to PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True  # Checks if the DB connection is alive before using it
)

# SessionLocal is a factory for creating individual database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    FastAPI dependency that provides a transactional database session.
    Closes the session cleanly once the API request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
