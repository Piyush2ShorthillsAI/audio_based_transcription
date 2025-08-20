# PostgreSQL Database Setup Guide

This guide will help you set up PostgreSQL for the CRM Authentication System.

## 🐘 Install PostgreSQL

### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

### macOS (using Homebrew):
```bash
brew install postgresql
brew services start postgresql
```

### Windows:
Download and install from [PostgreSQL official website](https://www.postgresql.org/download/windows/)

## 🔧 Database Configuration

### 1. Start PostgreSQL Service
```bash
# Ubuntu/Debian
sudo systemctl start postgresql
sudo systemctl enable postgresql

# macOS
brew services start postgresql
```

### 2. Create Database User and Database
```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL shell:
CREATE DATABASE crm_auth;
CREATE USER postgres WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE crm_auth TO postgres;
\q
```

### 3. Set Environment Variable (Optional)
If you want to use different database credentials:

```bash
# Linux/macOS
export DATABASE_URL="postgresql://username:password@localhost/database_name"

# Windows
set DATABASE_URL="postgresql://username:password@localhost/database_name"
```

## 🚀 Setup Database Tables

Run the setup script to create tables:

```bash
cd backend
python setup_db.py
```

## 🔍 Verify Setup

Check if tables were created:

```bash
sudo -u postgres psql crm_auth

# In PostgreSQL shell:
\dt              # List all tables
\d users         # Describe users table
\d sessions      # Describe sessions table
\q
```

## 📊 Database Schema

### Users Table
- `id` (UUID, Primary Key)
- `username` (VARCHAR 50, Unique)
- `email` (VARCHAR 100, Unique) 
- `password` (VARCHAR 255, Hashed)
- `photo_url` (VARCHAR 500, Nullable)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

### Sessions Table
- `id` (UUID, Primary Key)
- `user_id` (UUID, Foreign Key to users.id)
- `refresh_token` (TEXT, Unique)
- `created_at` (TIMESTAMP)
- `expires_at` (TIMESTAMP)
- `is_active` (VARCHAR 10)

## 🛠️ Troubleshooting

### Connection Issues:
1. Check if PostgreSQL is running: `sudo systemctl status postgresql`
2. Verify database exists: `sudo -u postgres psql -l`
3. Check credentials and database URL

### Permission Issues:
```bash
# Grant permissions to user
sudo -u postgres psql
GRANT ALL PRIVILEGES ON DATABASE crm_auth TO postgres;
```

### Reset Database (if needed):
```bash
sudo -u postgres psql
DROP DATABASE crm_auth;
CREATE DATABASE crm_auth;
```

## 🔄 Alternative: Using Docker

If you prefer Docker:

```bash
# Run PostgreSQL in Docker
docker run --name postgres-crm \
  -e POSTGRES_DB=crm_auth \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  -d postgres:13

# Then run setup
python setup_db.py
```

## ✅ Ready to Go!

Once setup is complete, start your FastAPI server:

```bash
source venv/bin/activate
uvicorn main:app --reload
```

Your authentication system will now use PostgreSQL for persistent data storage! 🎉