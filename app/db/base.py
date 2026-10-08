from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy database models.
    Every model class will inherit from this Base.
    """
    pass
