#!/usr/bin/env python3
"""
Database migration script to add recent contacts and favorites tables
Run this script to update your existing database with the new tables.
"""

import asyncio
from .database import database, connect_db, disconnect_db, engine
from sqlalchemy import text


async def create_recents_favorites_tables():
    """Create the new tables for recent contacts and favorites"""
    try:
        print("🚀 Adding recent contacts and favorites tables...")
        
        # Connect to database
        await connect_db()
        
        # Create user_recent_contacts table and indexes (execute separately)
        sql_commands = [
            """CREATE TABLE IF NOT EXISTS user_recent_contacts (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                contact_id UUID NOT NULL REFERENCES crm_contacts(id) ON DELETE CASCADE,
                accessed_at TIMESTAMP DEFAULT NOW() NOT NULL,
                UNIQUE(user_id, contact_id)
            )""",
            "CREATE INDEX IF NOT EXISTS idx_user_recent_contacts_user_id ON user_recent_contacts(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_recent_contacts_contact_id ON user_recent_contacts(contact_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_recent_contacts_accessed_at ON user_recent_contacts(accessed_at DESC)",
            """CREATE TABLE IF NOT EXISTS user_favorites (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                contact_id UUID NOT NULL REFERENCES crm_contacts(id) ON DELETE CASCADE,
                created_at TIMESTAMP DEFAULT NOW() NOT NULL,
                UNIQUE(user_id, contact_id)
            )""",
            "CREATE INDEX IF NOT EXISTS idx_user_favorites_user_id ON user_favorites(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_favorites_contact_id ON user_favorites(contact_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_favorites_created_at ON user_favorites(created_at DESC)"
        ]
        
        # Execute each SQL command separately
        for sql_command in sql_commands:
            await database.execute(text(sql_command))
        
        print("✅ Successfully created tables:")
        print("   - user_recent_contacts (stores recently viewed contacts)")
        print("   - user_favorites (stores favorite contacts)")
        print("   - All necessary indexes created")
        
        # Disconnect
        await disconnect_db()
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        print("\nPlease ensure:")
        print("1. PostgreSQL is running")
        print("2. Database 'crm_auth' exists")
        print("3. Existing tables (users, crm_contacts) are present")
        
        await disconnect_db()
        raise


async def verify_tables():
    """Verify that the new tables were created successfully"""
    try:
        await connect_db()
        
        # Check if tables exist
        check_tables_sql = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('user_recent_contacts', 'user_favorites')
        ORDER BY table_name;
        """
        
        results = await database.fetch_all(check_tables_sql)
        table_names = [row['table_name'] for row in results]
        
        if 'user_recent_contacts' in table_names and 'user_favorites' in table_names:
            print("✅ Verification successful: Both tables exist")
            
            # Check table structures
            for table_name in ['user_recent_contacts', 'user_favorites']:
                columns_sql = f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position;
                """
                columns = await database.fetch_all(columns_sql)
                print(f"\n📋 Table '{table_name}' structure:")
                for col in columns:
                    print(f"   - {col['column_name']}: {col['data_type']} ({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")
        else:
            missing = [t for t in ['user_recent_contacts', 'user_favorites'] if t not in table_names]
            print(f"❌ Missing tables: {missing}")
            
        await disconnect_db()
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        await disconnect_db()


async def main():
    """Main migration function"""
    print("=" * 60)
    print("🔧 CRM Database Migration: Adding Recents & Favorites")
    print("=" * 60)
    
    try:
        await create_recents_favorites_tables()
        print("\n" + "=" * 60)
        print("🔍 Verifying Migration...")
        print("=" * 60)
        await verify_tables()
        
        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        print("=" * 60)
        print("\n📚 Next Steps:")
        print("1. Restart your FastAPI server")
        print("2. Update frontend to use new backend endpoints")
        print("3. Test the recent contacts and favorites functionality")
        print("\n🎯 New API Endpoints Available:")
        print("   POST   /recents/{contact_id}    - Add to recent contacts")
        print("   GET    /recents                 - Get recent contacts")
        print("   DELETE /recents                 - Clear recent contacts")
        print("   POST   /favorites/{contact_id}  - Add to favorites")
        print("   DELETE /favorites/{contact_id}  - Remove from favorites")
        print("   GET    /favorites               - Get favorites")
        print("   DELETE /favorites               - Clear favorites")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())