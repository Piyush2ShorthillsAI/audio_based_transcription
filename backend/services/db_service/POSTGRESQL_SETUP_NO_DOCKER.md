# PostgreSQL Setup (Without Docker)

This guide shows how to set up PostgreSQL for your application without using Docker.

## Option 1: Install PostgreSQL Locally (Recommended)

### Ubuntu/Debian Installation

```bash
# Update package list
sudo apt update

# Install PostgreSQL and additional tools
sudo apt install postgresql postgresql-contrib postgresql-client

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql  # Auto-start on boot

# Check status
sudo systemctl status postgresql
```

### Create Database and User

```bash
# Switch to postgres user
sudo -u postgres psql

# Inside PostgreSQL shell:
CREATE DATABASE crm_auth;
CREATE USER postgres WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE crm_auth TO postgres;

# Make user a superuser (for table creation)
ALTER USER postgres CREATEDB;

# Exit PostgreSQL shell
\q
```

### Test Connection

```bash
# Test connection
psql -h localhost -U postgres -d crm_auth -c "SELECT version();"
```

## Option 2: Use Existing PostgreSQL

If you already have PostgreSQL installed:

```bash
# Create the database
createdb -U your_username crm_auth

# Or using psql:
psql -U your_username -c "CREATE DATABASE crm_auth;"
```

## Option 3: Online PostgreSQL Service (For Testing)

For quick testing, you can use free online PostgreSQL services:

1. **Aiven** (Free tier): https://aiven.io/
2. **ElephantSQL** (Free tier): https://www.elephantsql.com/
3. **Supabase** (Free tier): https://supabase.com/

## Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# For local PostgreSQL
DATABASE_URL=postgresql://postgres:password@localhost:5432/crm_auth

# For online service (example)
# DATABASE_URL=postgresql://username:password@hostname:5432/database_name

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Update Database Configuration

The application is already configured to use PostgreSQL. You can customize the connection in `services/db_service/database.py`:

```python
# Default connection (can be overridden by environment variable)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/crm_auth")
```

## Testing the Setup

### 1. Test Database Connection

```bash
cd backend

# Simple connection test
python3 -c "
import asyncio
from services.db_service.database import connect_db, disconnect_db, create_tables

async def test_db():
    try:
        await connect_db()
        print('✅ Connected to PostgreSQL successfully!')
        create_tables()
        print('✅ Tables created successfully!')
        await disconnect_db()
        print('✅ Disconnected successfully!')
    except Exception as e:
        print(f'❌ Error: {e}')

asyncio.run(test_db())
"
```

### 2. Start the Application

```bash
# Install dependencies (already done)
pip install -r requirements.txt

# Start the server
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Test User Registration

```bash
# Test signup endpoint
curl -X POST http://127.0.0.1:8000/auth/signup \
  -H "Content-Type: multipart/form-data" \
  -F "username=testuser" \
  -F "email=test@example.com" \
  -F "password=testpass123"
```

## Troubleshooting

### PostgreSQL Not Starting

```bash
# Check status
sudo systemctl status postgresql

# Start manually
sudo systemctl start postgresql

# Check logs
sudo journalctl -u postgresql
```

### Connection Refused

```bash
# Check if PostgreSQL is listening
sudo netstat -plunt | grep 5432

# Check PostgreSQL configuration
sudo nano /etc/postgresql/*/main/postgresql.conf
# Ensure: listen_addresses = 'localhost'

sudo nano /etc/postgresql/*/main/pg_hba.conf
# Ensure: local   all   postgres   trust
#         host    all   all        127.0.0.1/32   md5
```

### Authentication Issues

```bash
# Reset postgres password
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'password';"

# Or create a new user
sudo -u postgres createuser --interactive --pwprompt myuser
```

### Permission Denied

```bash
# Check PostgreSQL is running as correct user
ps aux | grep postgres

# Fix permissions
sudo chown -R postgres:postgres /var/lib/postgresql
sudo chmod -R 750 /var/lib/postgresql
```

## Alternative: Keep Using SQLite (Temporary)

If you prefer to continue with SQLite for now, simply change the database URL back:

```python
# In services/db_service/database.py
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
```

And revert the models to use String UUIDs (as they were working before).

## Next Steps

1. Install PostgreSQL locally: `sudo apt install postgresql`
2. Create database and user
3. Test connection with the Python script above
4. Start your application: `uvicorn main:app --reload`
5. Test signup functionality

The application will automatically create the required tables on startup!