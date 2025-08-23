#!/usr/bin/env python3

"""
Migration script to add simplified favorites and recents fields to crm_contacts table
This replaces the complex separate tables approach with simple boolean/timestamp fields
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import database, connect_db, disconnect_db
from sqlalchemy import text

async def migrate_add_simple_favorites():
    """Add is_favorite and last_accessed_at fields to crm_contacts table"""
    
    print("🔄 Adding simplified favorites and recents fields to crm_contacts...")
    print("=" * 60)
    
    try:
        # Connect to database
        await connect_db()
        print("🔗 Connected to PostgreSQL database")
        
        # SQL commands to add the new fields
        migration_commands = [
            # Add is_favorite boolean field with default False
            """
            ALTER TABLE crm_contacts 
            ADD COLUMN IF NOT EXISTS is_favorite BOOLEAN DEFAULT FALSE NOT NULL;
            """,
            
            # Add last_accessed_at timestamp field
            """
            ALTER TABLE crm_contacts 
            ADD COLUMN IF NOT EXISTS last_accessed_at TIMESTAMP;
            """,
            
            # Add indexes for performance
            """
            CREATE INDEX IF NOT EXISTS idx_crm_contacts_is_favorite 
            ON crm_contacts(is_favorite) WHERE is_favorite = true;
            """,
            
            """
            CREATE INDEX IF NOT EXISTS idx_crm_contacts_last_accessed 
            ON crm_contacts(last_accessed_at DESC) WHERE last_accessed_at IS NOT NULL;
            """,
            
            # Add compound index for user + favorite filtering
            """
            CREATE INDEX IF NOT EXISTS idx_crm_contacts_user_favorite 
            ON crm_contacts(user_id, is_favorite) WHERE is_favorite = true;
            """
        ]
        
        # Execute each command separately
        for i, sql_command in enumerate(migration_commands, 1):
            try:
                await database.execute(text(sql_command))
                print(f"✅ Migration step {i}/5 completed")
            except Exception as e:
                print(f"⚠️ Migration step {i}/5 warning: {e}")
                # Continue with other commands even if one fails
        
        # Verify the fields were added
        print("\n🔍 Verifying migration...")
        
        # Check if columns exist
        verify_query = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = 'crm_contacts' 
        AND column_name IN ('is_favorite', 'last_accessed_at')
        ORDER BY column_name;
        """
        
        columns = await database.fetch_all(text(verify_query))
        
        if len(columns) >= 2:
            print("✅ Migration successful! New fields added:")
            for col in columns:
                print(f"   - {col['column_name']}: {col['data_type']} (default: {col['column_default']})")
        else:
            print("❌ Migration verification failed - fields not found")
            return False
            
        # Show current table structure
        print("\n📋 Current crm_contacts table structure:")
        structure_query = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = 'crm_contacts' 
        ORDER BY ordinal_position;
        """
        
        all_columns = await database.fetch_all(text(structure_query))
        for col in all_columns:
            nullable = "NULL" if col['is_nullable'] == "YES" else "NOT NULL"
            default = f" (default: {col['column_default']})" if col['column_default'] else ""
            print(f"   - {col['column_name']}: {col['data_type']} {nullable}{default}")
        
        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        print("=" * 60)
        
        print("\n📚 Next Steps:")
        print("1. Restart your FastAPI server")
        print("2. Update frontend to use the new simplified approach")
        print("3. Test favorites functionality")
        
        print("\n🎯 New Simplified Approach:")
        print("   - Favorites: is_favorite boolean field in crm_contacts")
        print("   - Recents: last_accessed_at timestamp field in crm_contacts")
        print("   - No more separate tables needed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        await disconnect_db()
        print("\n📴 Disconnected from PostgreSQL database")

if __name__ == "__main__":
    success = asyncio.run(migrate_add_simple_favorites())
    if success:
        print("🎉 Migration completed successfully!")
        sys.exit(0)
    else:
        print("💥 Migration failed!")
        sys.exit(1)