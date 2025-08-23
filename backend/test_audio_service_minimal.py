#!/usr/bin/env python3
"""Comprehensive test for audio_service_minimal.py"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent))

async def test_audio_service_minimal():
    """Test all functionality of AudioServiceMinimal"""
    print("🧪 TESTING AUDIO SERVICE MINIMAL")
    print("=" * 80)
    
    try:
        # Import required modules
        from services.db_service.database import get_database
        from services.audio_service.audio_service_minimal import AudioServiceMinimal
        
        # Connect to database
        print("🔗 Connecting to database...")
        database = await get_database()
        print("✅ Database connected successfully")
        
        # Initialize AudioServiceMinimal
        print("\n🚀 Initializing AudioServiceMinimal...")
        audio_service = AudioServiceMinimal(database)
        print("✅ AudioServiceMinimal initialized successfully")
        
        # Test 1: Get user recordings
        print("\n" + "=" * 50)
        print("📋 TEST 1: Get User Recordings")
        print("=" * 50)
        
        test_user_id = "test-user-123"
        recordings = await audio_service.get_user_recordings(test_user_id)
        print(f"📊 Found {len(recordings)} recordings for user {test_user_id}")
        
        if recordings:
            print("🎵 Sample recordings:")
            for i, recording in enumerate(recordings[:3]):  # Show first 3
                print(f"  {i+1}. ID: {recording['id'][:8]}... | Title: {recording.get('title', 'N/A')}")
        else:
            print("📝 No recordings found (this is normal for test user)")
        
        # Test 2: Check if we have any audio files to test with
        print("\n" + "=" * 50)
        print("📋 TEST 2: Check Available Audio Files")  
        print("=" * 50)
        
        audio_dir = Path("uploads/audio")
        if audio_dir.exists():
            mp3_files = list(audio_dir.glob("*.mp3"))
            webm_files = list(audio_dir.glob("*.webm"))
            
            print(f"📁 Found {len(mp3_files)} MP3 files")
            print(f"📁 Found {len(webm_files)} WebM files")
            
            if len(mp3_files) >= 2:
                # Test 3: Email generation with real files
                print("\n" + "=" * 50)
                print("📋 TEST 3: Email Generation from Audio Files")
                print("=" * 50)
                
                file1 = str(mp3_files[0])
                file2 = str(mp3_files[1])
                
                print(f"🎵 Testing with:")
                print(f"   Relationship: {file1}")
                print(f"   Content: {file2}")
                
                # First, let's check if there are any recordings in the database we can use
                all_recordings_query = """
                SELECT id, user_id, file_path, title FROM audio_recordings 
                ORDER BY created_at DESC LIMIT 10
                """
                existing_recordings = await database.fetch_all(all_recordings_query)
                
                if len(existing_recordings) >= 2:
                    print(f"\n✅ Found {len(existing_recordings)} existing recordings in database")
                    
                    # Use first two recordings for testing
                    recording1 = existing_recordings[0]
                    recording2 = existing_recordings[1]
                    
                    print(f"📊 Using recordings:")
                    print(f"   Recording 1: {recording1['id'][:8]}... ({recording1.get('title', 'N/A')})")
                    print(f"   Recording 2: {recording2['id'][:8]}... ({recording2.get('title', 'N/A')})")
                    
                    # Test email generation
                    print(f"\n🤖 Generating email...")
                    result = await audio_service.generate_email_from_dual_audio_direct(
                        relationship_recording_id=recording1['id'],
                        content_recording_id=recording2['id'],
                        user_id=recording1['user_id'],
                        recipient_name="Test User",
                        recipient_email="test@example.com",
                        relationship="professional"
                    )
                    
                    print(f"\n✅ Email generation completed!")
                    print(f"📊 Result keys: {list(result.keys())}")
                    print(f"📝 Email body length: {len(result.get('email', {}).get('body', ''))}")
                    
                    if 'email' in result and 'body' in result['email']:
                        body = result['email']['body']
                        preview = body[:200] + "..." if len(body) > 200 else body
                        print(f"📄 Email preview: {preview}")
                    
                else:
                    print("⚠️  Not enough recordings in database to test email generation")
                    print("💡 Upload some audio files from frontend first")
            
            else:
                print("⚠️  Need at least 2 MP3 files for email generation test")
                print(f"💡 Found {len(mp3_files)} MP3 files, need 2")
        
        else:
            print("❌ uploads/audio directory not found")
        
        # Test 4: Database connection check
        print("\n" + "=" * 50)
        print("📋 TEST 4: Database Connection Test")
        print("=" * 50)
        
        # Test simple query
        result = await database.fetch_one("SELECT COUNT(*) as count FROM audio_recordings")
        total_recordings = result['count'] if result else 0
        print(f"📊 Total recordings in database: {total_recordings}")
        
        # Test user-specific query  
        user_count_query = """
        SELECT user_id, COUNT(*) as count FROM audio_recordings 
        GROUP BY user_id ORDER BY count DESC LIMIT 5
        """
        user_stats = await database.fetch_all(user_count_query)
        
        if user_stats:
            print(f"👥 Top users by recordings:")
            for stat in user_stats:
                user_id = stat['user_id'][:8] + "..." if len(stat['user_id']) > 8 else stat['user_id']
                print(f"   {user_id}: {stat['count']} recordings")
        else:
            print("📝 No user statistics available")
        
        print("\n" + "=" * 80)
        print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        
        # Close database connection
        await database.disconnect()
        print("📴 Database disconnected")
        
    except Exception as e:
        print(f"\n❌ ERROR DURING TESTING!")
        print(f"🔍 Error type: {type(e).__name__}")
        print(f"📝 Error message: {str(e)}")
        
        import traceback
        print("\n📊 Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_audio_service_minimal())