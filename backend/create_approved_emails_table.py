#!/usr/bin/env python3
"""
Simple script to create approved_emails table
"""

import asyncio
from services.db_service.database import database

async def create_approved_emails_table():
    """Create approved_emails table with three foreign keys"""
    
    await database.connect()
    
    try:
        print("Creating approved_emails table...")
        
        query = """
        CREATE TABLE IF NOT EXISTS approved_emails (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id),
            contact_id UUID NOT NULL REFERENCES crm_contacts(id), 
            recording_id UUID NOT NULL REFERENCES audio_recordings(id),
            email_content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """
        
        await database.execute(query)
        print("✅ approved_emails table created successfully")
        
    finally:
        await database.disconnect()

if __name__ == "__main__":
    asyncio.run(create_approved_emails_table())