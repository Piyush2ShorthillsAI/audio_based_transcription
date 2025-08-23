#!/usr/bin/env python3
"""
Database setup script for CRM Authentication System
This script creates the necessary database and tables for the application.
"""

import asyncio
import os
from .database import database, create_tables, connect_db, disconnect_db

async def setup_database():
    """Setup the database and create tables"""
    try:
        print("🚀 Setting up PostgreSQL database...")
        
        # Connect to database
        await connect_db()
        
        # Create tables
        create_tables()
        
        print("✅ Database setup completed successfully!")
        print("📊 Created tables:")
        print("   - users (stores user accounts)")
        print("   - sessions (stores authentication sessions)")
        
        # Disconnect
        await disconnect_db()
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        print("\nPlease ensure:")
        print("1. PostgreSQL is installed and running")
        print("2. Database 'crm_auth' exists")
        print("3. User 'postgres' has access with password 'password'")
        print("4. Or set DATABASE_URL environment variable")

def show_database_info():
    """Show database configuration information"""
    db_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost/crm_auth")
    print("🔗 Database Configuration:")
    print(f"   URL: {db_url}")
    print()

if __name__ == "__main__":
    show_database_info()
    asyncio.run(setup_database())