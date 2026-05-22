from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


eng = create_engine(
    "postgresql://postgres:Abhyudit8520@localhost:5432/test")

SessionLocal = sessionmaker(bind=eng)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()