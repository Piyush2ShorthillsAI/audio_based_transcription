# Database Service Package

This package contains all database-related functionality for the CRM Authentication System.

## 📁 Files Structure

```
db_service/
├── __init__.py         # Package initialization and exports
├── database.py         # Database connection and configuration
├── models.py          # SQLAlchemy models (User, Session)
├── setup_db.py        # Database setup script
└── README.md          # This documentation
```

## 📊 File Descriptions

### `database.py`
- **Purpose**: Database connection management and configuration
- **Contains**: 
  - Database URL configuration
  - Connection/disconnection functions
  - Table creation functionality
  - SQLAlchemy engine and metadata setup

### `models.py`
- **Purpose**: Database table definitions using SQLAlchemy ORM
- **Contains**:
  - `User` model: User accounts with authentication data
  - `Session` model: Authentication session management
  - Helper methods for data conversion

### `setup_db.py`
- **Purpose**: Database initialization and table creation script
- **Usage**: Run `python -m db_service.setup_db` from backend directory
- **Functions**: Creates database tables and verifies connectivity

### `__init__.py`
- **Purpose**: Makes the directory a Python package
- **Exports**: All commonly used functions and classes for easy importing

## 🚀 Usage Examples

### Import Database Components
```python
from db_service import database, User, Session, create_tables
```

### Setup Database
```bash
cd backend
python -m db_service.setup_db
```

### Use in FastAPI
```python
from db_service import database, connect_db, disconnect_db

@app.on_event("startup")
async def startup():
    await connect_db()

@app.on_event("shutdown") 
async def shutdown():
    await disconnect_db()
```

## 🔗 Dependencies
- PostgreSQL database server
- SQLAlchemy for ORM
- asyncpg for async PostgreSQL operations
- databases library for async database operations