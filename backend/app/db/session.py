from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# We default to sqlite for absolute straightforward usability right out of the box
SQLALCHEMY_DATABASE_URL = "sqlite:///./intent_hire.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to yield session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
