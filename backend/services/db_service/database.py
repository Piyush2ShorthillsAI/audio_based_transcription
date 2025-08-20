import os
from databases import Database
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# For async operations
database = Database(DATABASE_URL)

# For SQLAlchemy models
engine = create_engine(DATABASE_URL)
metadata = MetaData()
Base = declarative_base(metadata=metadata)

# For sync operations (if needed)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def connect_db():
    """Connect to the database"""
    await database.connect()
    print("🔗 Connected to SQLite database")

async def disconnect_db():
    """Disconnect from the database"""
    await database.disconnect()
    print("📴 Disconnected from SQLite database")

def create_tables():
    """Create all tables"""
    metadata.create_all(bind=engine)
    print("📊 Database tables created successfully")

# Database dependency for FastAPI
async def get_database():
    """Dependency to get database connection"""
    return database