from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/image_db")

# Extract DB connection info (assuming PostgreSQL)
DEFAULT_DB_URL = "postgresql://postgres:postgres@localhost/postgres"  # Connect to default "postgres" DB
DB_NAME = "image_db"

# Create an engine to check if the database exists
default_engine = create_engine(DEFAULT_DB_URL, isolation_level="AUTOCOMMIT")

with default_engine.connect() as conn:
    result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname='{DB_NAME}'"))
    if not result.fetchone():
        conn.execute(text(f"CREATE DATABASE {DB_NAME}"))
        print(f"Database '{DB_NAME}' created successfully!")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency function to get a database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize the database and create tables"""
    from models import ImageProcessingRequest  # Import models inside the function to avoid circular imports
    Base.metadata.create_all(bind=engine)
