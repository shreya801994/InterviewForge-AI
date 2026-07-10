from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from typing import Generator
from app.config import settings

# Determine database engine arguments based on database URL
db_url = settings.get_db_url
connect_args = {}
engine_kwargs = {"pool_pre_ping": True}

if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    # PostgreSQL / Supabase pool limits optimization
    engine_kwargs.update({
        "pool_size": 5,
        "max_overflow": 10,
        "pool_recycle": 1800
    })

# Create engine
engine = create_engine(
    db_url,
    connect_args=connect_args,
    **engine_kwargs
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Declarative Base for models
class Base(DeclarativeBase):
    pass

def get_db() -> Generator:
    """Dependency injection helper to yield database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
