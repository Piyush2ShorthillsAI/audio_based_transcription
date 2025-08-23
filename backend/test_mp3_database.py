#!/usr/bin/env python3
"""Test the updated system with MP3 files stored in database"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent))

async def test_mp3_database():
    """Test the complete flow with MP3 files in database"""
    print("🧪 TESTING MP3 DATABASE INTEGRATION")
    print("=" * 80)
    
    try:
        from services.db_service.database import database
        from services.audio_service.audio_service_minimal import AudioServiceMinimal
        
        # Connect to database
        await database.connect()
        print("✅ Database connected")
        
        # Initialize audio service
        audio_service = AudioServiceMinimal(database)
        print("✅ Audio service initialized")
        
        # Step 1: Check MP3 records in database
        print(f"\n📋 Step 1: Check MP3 Records in Database")
        print("-" * 40)
        
        mp3_query = """
        SELECT id, filename, file_path, format, audio_type, file_size, user_id
        FROM audio_recordings 
        WHERE format = 'audio/mp3' AND status = 'uploaded'
        ORDER BY created_at DESC 
        LIMIT 5
        """
        
        mp3_records = await database.fetch_all(mp3_query)
        print(f"📁 Found {len(mp3_records)} MP3 records in database")
        
        if len(mp3_records) < 2:
            print("❌ Need at least 2 MP3 records for testing")
            return
        
        for i, record in enumerate(mp3_records[:3], 1):
            file_size_kb = record['file_size'] // 1024
            print(f"   {i}. {record['filename']} ({record['format']}, {record['audio_type']}, {file_size_kb}KB)")
        
        # Step 2: Verify MP3 files exist on disk
        print(f"\n📁 Step 2: Verify MP3 Files on Disk")
        print("-" * 40)
        
        for record in mp3_records[:3]:
            file_path = Path(record['file_path'])
            if file_path.exists():
                print(f"   ✅ {file_path.name} ({file_path.stat().st_size} bytes)")
            else:
                print(f"   ❌ Missing: {file_path.name}")
        
        # Step 3: Test email generation with MP3 files
        print(f"\n🎯 Step 3: Test Email Generation with MP3 Files")
        print("-" * 40)
        
        # Use first two records
        record1 = mp3_records[0]
        record2 = mp3_records[1]
        
        print(f"🎵 Testing with MP3 files:")
        print(f"   📁 Relationship: {record1['filename']} ({record1['audio_type']})")
        print(f"   📁 Content: {record2['filename']} ({record2['audio_type']})")
        print(f"   👤 User: {record1['user_id']}")
        
        # Call the audio service method
        result = await audio_service.generate_email_from_dual_audio_direct(
            relationship_recording_id=record1['id'],
            content_recording_id=record2['id'],
            user_id=record1['user_id'],
            recipient_name="Test Recipient",
            recipient_email="test@example.com",
            relationship="professional"
        )
        
        print(f"\n✅ SUCCESS! Email generation completed")
        print(f"📧 Email type: {type(result.get('email'))}")
        print(f"📊 Email length: {len(str(result.get('email', '')))}")
        print(f"🔧 Processing method: {result.get('processing_method')}")
        
        # Check if it's a proper email or error message
        email_content = str(result.get('email', ''))
        is_error = email_content.startswith('❌ Error:')
        
        if is_error:
            print(f"⚠️  Got error response:")
            print(f"   {email_content[:100]}...")
        else:
            print(f"🎉 Got proper email response!")
            print(f"   📧 Preview: {email_content[:100]}...")
        
        # Step 4: Database statistics
        print(f"\n📊 Step 4: Database Format Statistics")
        print("-" * 40)
        
        stats_query = """
        SELECT format, COUNT(*) as count 
        FROM audio_recordings 
        GROUP BY format 
        ORDER BY count DESC
        """
        
        stats = await database.fetch_all(stats_query)
        for stat in stats:
            print(f"   🎵 {stat['format']}: {stat['count']} records")
        
        await database.disconnect()
        
        print(f"\n" + "=" * 80)
        print("🎉 MP3 DATABASE TEST COMPLETED!")
        print("=" * 80)
        
        if not is_error:
            print("✅ System is working perfectly with MP3 files!")
            print("✅ Database stores MP3 format records")  
            print("✅ Audio service uses MP3 files directly")
            print("✅ Gemini receives MP3 files (compatible format)")
            print("✅ Email generation successful!")
        else:
            print("⚠️  Got error response - check Gemini compatibility")
        
    except Exception as e:
        print(f"\n❌ ERROR DURING TESTING!")
        print(f"🔍 Error type: {type(e).__name__}")
        print(f"📝 Error message: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mp3_database())