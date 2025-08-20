# Services Package

This package contains all service-related functionality for the CRM Authentication System, organized into specialized service modules.

## 📁 Services Structure

```
services/
├── __init__.py                    # Main services package exports
├── README.md                      # This documentation
├── authservice/                   # Authentication Service
│   ├── __init__.py               # Auth service exports
│   └── authservice.py            # Authentication logic
└── db_service/                   # Database Service  
    ├── __init__.py               # DB service exports
    ├── database.py               # Database connection
    ├── models.py                 # SQLAlchemy models
    ├── setup_db.py               # Database setup
    └── README.md                 # DB service documentation
```

## 🔧 Service Modules

### 🔐 AuthService (`authservice/`)
**Purpose**: Handles all authentication and user management operations
- **User Registration**: Signup with optional photo upload
- **Authentication**: Login with email/username + password  
- **Session Management**: JWT tokens and refresh tokens
- **Password Security**: Bcrypt hashing and verification
- **User Operations**: Profile management and logout

**Key Components**:
- `AuthService` class with async database operations
- Pydantic models for request/response validation
- JWT token creation and verification
- PostgreSQL integration for persistent storage

### 🗄️ Database Service (`db_service/`)
**Purpose**: Manages all database operations and configurations
- **Database Connection**: PostgreSQL async connection management
- **Models**: SQLAlchemy ORM models for User and Session tables  
- **Setup Scripts**: Database initialization and table creation
- **Configuration**: Database URL and connection parameters

**Key Components**:
- `User` and `Session` SQLAlchemy models
- Database connection lifecycle management
- Table creation and migration utilities
- PostgreSQL-specific configurations

## 🚀 Usage Examples

### Import Services
```python
# Import from main services package
from services import AuthService, database, User

# Import from specific service modules  
from services.authservice import AuthService, UserSignup
from services.db_service import database, User, Session
```

### Use in FastAPI Application
```python
from services.db_service import connect_db, disconnect_db
from services.authservice import AuthService

@app.on_event("startup")
async def startup():
    await connect_db()

@app.on_event("shutdown")
async def shutdown():
    await disconnect_db()
```

### Database Setup
```bash
# Run database setup from backend directory
cd backend
python -m services.db_service.setup_db
```

## 🏗️ Architecture Benefits

1. **🧩 Separation of Concerns**: Each service handles specific functionality
2. **📦 Modular Design**: Services can be developed and tested independently  
3. **🔄 Scalability**: Easy to add new services (e.g., email, notifications)
4. **📁 Organization**: Clear structure for different types of operations
5. **🛠️ Maintainability**: Isolated code makes debugging and updates easier

## 🔗 Inter-Service Communication

- **AuthService** uses **Database Service** for user data persistence
- **Database Service** provides models and connection management
- **Main App** orchestrates services through dependency injection
- Clean interfaces between services prevent tight coupling

## 📋 Adding New Services

To add a new service:

1. **Create Service Folder**: `services/new_service/`
2. **Add Service Logic**: `new_service/new_service.py`
3. **Create Package Init**: `new_service/__init__.py` 
4. **Update Main Init**: Add exports to `services/__init__.py`
5. **Add Documentation**: Create `new_service/README.md`

## 🔧 Dependencies

- **FastAPI**: Web framework and dependency injection
- **PostgreSQL**: Database server
- **SQLAlchemy**: ORM for database operations  
- **asyncpg**: Async PostgreSQL driver
- **bcrypt**: Password hashing
- **python-jose**: JWT token management