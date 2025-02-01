import os
from sqlalchemy import create_engine
from sqlalchemy.engine import URL  # Available in SQLAlchemy 1.4+
from sqlalchemy.orm import sessionmaker
from models import Base  # Assuming your models are in models.py

# Parse individual credentials from environment variables.
postgres_user = os.getenv("POSTGRES_USER", "user")
postgres_password = os.getenv("POSTGRES_PASSWORD", "password")
postgres_db = os.getenv("POSTGRES_DB", "rooms_db")
# Use service name from docker-compose
postgres_host = os.getenv("POSTGRES_HOST", "postgres")
postgres_port = os.getenv("POSTGRES_PORT", "5432")

# Construct the connection URL.
db_url = URL.create(
    drivername="postgresql",
    username=postgres_user,
    password=postgres_password,
    host=postgres_host,
    port=postgres_port,
    database=postgres_db
)

# Create the SQLAlchemy engine.
engine = create_engine(db_url)

# Create a configured "Session" class.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# (Optional) Create tables if they do not exist. In production, use migrations.
Base.metadata.create_all(bind=engine)
