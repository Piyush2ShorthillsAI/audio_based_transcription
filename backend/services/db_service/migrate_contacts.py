#!/usr/bin/env python3
"""
Database migration script to add user_id column to crm_contacts table.
This script safely adds the user_id foreign key to existing contacts.
"""

import asyncio
import sys
import os
from typing import Optional

# Add the parent directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from services.db_service.database import database, connect_db, disconnect_db


async def get_first_user_id() -> Optional[str]:
    """Get the first user ID from the users table to assign to existing contacts."""
    try:
        query = "SELECT id FROM users LIMIT 1"
        result = await database.fetch_one(query)
        return str(result["id"]) if result else None
    except Exception as e:
        print(f"❌ Error fetching user ID: {e}")
        return None


async def add_user_id_column():
    """Add user_id column to crm_contacts table and populate with first user."""
    try:
        print("🔧 Starting migration: Adding user_id column to crm_contacts...")
        
        # First, check if the column already exists
        check_column_query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'crm_contacts' AND column_name = 'user_id'
        """
        
        existing_column = await database.fetch_one(check_column_query)
        
        if existing_column:
            print("✅ user_id column already exists in crm_contacts table")
            return True
            
        # Get first user ID to assign to existing contacts
        first_user_id = await get_first_user_id()
        
        if not first_user_id:
            print("⚠️  No users found in database. Please create a user first.")
            print("   Existing contacts will need to be manually assigned to users.")
            print("   Adding column as nullable for now...")
            
            # Add column as nullable if no users exist
            add_column_query = """
            ALTER TABLE crm_contacts 
            ADD COLUMN user_id UUID REFERENCES users(id);
            """
        else:
            # Add column as NOT NULL with default value
            add_column_query = f"""
            ALTER TABLE crm_contacts 
            ADD COLUMN user_id UUID NOT NULL DEFAULT '{first_user_id}' REFERENCES users(id);
            """
            
        await database.execute(add_column_query)
        print("✅ Successfully added user_id column to crm_contacts table")
        
        # Create index on user_id for performance
        index_query = "CREATE INDEX IF NOT EXISTS idx_crm_contacts_user_id ON crm_contacts(user_id);"
        await database.execute(index_query)
        print("✅ Created index on user_id column")
        
        # Show summary of changes
        count_query = "SELECT COUNT(*) as total FROM crm_contacts"
        result = await database.fetch_one(count_query)
        total_contacts = result["total"] if result else 0
        
        if first_user_id and total_contacts > 0:
            print(f"📊 Assigned {total_contacts} existing contacts to user ID: {first_user_id}")
        else:
            print(f"📊 Migration complete. {total_contacts} contacts in database.")
            
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


async def verify_migration():
    """Verify that the migration was successful."""
    try:
        # Check if user_id column exists and has foreign key constraint
        verify_query = """
        SELECT 
            c.column_name,
            c.data_type,
            c.is_nullable,
            tc.constraint_type
        FROM information_schema.columns c
        LEFT JOIN information_schema.constraint_column_usage ccu 
            ON c.table_name = ccu.table_name AND c.column_name = ccu.column_name
        LEFT JOIN information_schema.table_constraints tc 
            ON ccu.constraint_name = tc.constraint_name
        WHERE c.table_name = 'crm_contacts' AND c.column_name = 'user_id'
        """
        
        result = await database.fetch_one(verify_query)
        
        if result:
            print("✅ Migration verification successful:")
            print(f"   - Column: {result['column_name']}")
            print(f"   - Type: {result['data_type']}")
            print(f"   - Nullable: {result['is_nullable']}")
            if result['constraint_type']:
                print(f"   - Constraint: {result['constraint_type']}")
            return True
        else:
            print("❌ Migration verification failed: user_id column not found")
            return False
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False


async def main():
    """Main migration function."""
    print("🚀 Starting crm_contacts migration...")
    
    try:
        # Connect to database
        await connect_db()
        print("🔗 Connected to database")
        
        # Run migration
        migration_success = await add_user_id_column()
        
        if migration_success:
            # Verify migration
            verification_success = await verify_migration()
            
            if verification_success:
                print("🎉 Migration completed successfully!")
                print("\n📝 Next steps:")
                print("   1. Restart your FastAPI server")
                print("   2. Update any contact creation endpoints to use current user ID")
                print("   3. Test the filtered contact retrieval")
            else:
                print("⚠️  Migration completed but verification failed")
                return False
        else:
            print("❌ Migration failed")
            return False
            
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return False
    finally:
        await disconnect_db()
        print("🔌 Disconnected from database")
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("CRM CONTACTS MIGRATION SCRIPT")
    print("Adding user_id column to crm_contacts table")
    print("=" * 60)
    
    success = asyncio.run(main())
    
    if success:
        print("\n✅ Migration script completed successfully")
        sys.exit(0)
    else:
        print("\n❌ Migration script failed")
        sys.exit(1)