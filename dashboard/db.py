# db.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# Example: get the database URL from an environment variable or use a default
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://user:password@localhost:5432/mydatabase")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# (Optional) Create tables if they do not exist. In production you may use migrations instead.
Base.metadata.create_all(bind=engine)
