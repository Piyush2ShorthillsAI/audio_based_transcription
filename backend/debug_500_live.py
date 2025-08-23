#!/usr/bin/env python3
"""Live debug for 500 error during email generation"""

import asyncio
import sys
import traceback
from pathlib import Path

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent))

from services.db_service.database import get_database
from services.audio_service.audio_service_minimal import AudioServiceMinimal

async def test_email_generation_live():
    """Test email generation with real uploaded files"""
    print("🔥 LIVE DEBUG: Email Generation 500 Error")
    print("=" * 50)
    
    try:
        # Connect to database
        print("🔗 Connecting to database...")
        database = await get_database()
        
        # Get recent audio recordings
        print("🎵 Checking recent audio uploads...")
        query = """
        SELECT id, user_id, contact_id, title, filename, file_path, status, created_at 
        FROM audio_recordings 
        WHERE status = 'uploaded' 
        ORDER BY created_at DESC 
        LIMIT 4
        """
        
        recent_recordings = await database.fetch_all(query)
        
        if not recent_recordings:
            print("❌ No recent audio recordings found")
            print("💡 Please upload some audio first from frontend")
            return
            
        print(f"✅ Found {len(recent_recordings)} recent recordings:")
        for i, recording in enumerate(recent_recordings):
            print(f"  {i+1}. ID: {recording['id'][:8]}... | Title: {recording['title']} | File: {recording['filename']}")
            
        if len(recent_recordings) < 2:
            print("❌ Need at least 2 recordings for dual email generation")
            return
            
        # Test with the 2 most recent recordings
        action_recording = recent_recordings[0]
        context_recording = recent_recordings[1]
        
        print(f"\n🎯 Testing dual email generation...")
        print(f"   Action: {action_recording['filename']}")
        print(f"   Context: {context_recording['filename']}")
        
        # Initialize AudioServiceMinimal
        print("\n🔧 Initializing AudioServiceMinimal...")
        audio_service = AudioServiceMinimal(database)
        
        # Test email generation
        print("\n🤖 Calling generate_email_from_dual_audio_direct...")
        
        result = await audio_service.generate_email_from_dual_audio_direct(
            relationship_recording_id=action_recording['id'],
            content_recording_id=context_recording['id'],
            user_id=action_recording['user_id'],
            contact_id=action_recording['contact_id'] or context_recording['contact_id'],
            recipient_name="Test Contact",
            recipient_email="test@example.com"
        )
        
        print("✅ EMAIL GENERATION SUCCESSFUL!")
        print(f"📧 Generated email length: {len(result.get('email', {}).get('full_content', 'N/A'))}")
        print(f"⏱️ Processing time: {result.get('metadata', {}).get('processing_time', 'N/A')}")
        print(f"🔄 Processing ID: {result.get('processing_id', 'N/A')}")
        
        await database.disconnect()
        
    except Exception as e:
        print(f"\n❌ ERROR FOUND!")
        print(f"🔍 Error type: {type(e).__name__}")
        print(f"📝 Error message: {str(e)}")
        print(f"\n📊 Full traceback:")
        traceback.print_exc()
        
        # Specific debugging for common issues
        if "DatabaseBackend is not running" in str(e):
            print("\n🔧 SOLUTION: Database connection issue")
            print("   - Restart the server")
            print("   - Check PostgreSQL is running")
            
        elif "gemini" in str(e).lower():
            print("\n🔧 SOLUTION: Gemini API issue")
            print("   - Check API key")
            print("   - Check audio file format")
            print("   - Check model name")
            
        elif "file" in str(e).lower():
            print("\n🔧 SOLUTION: File access issue")
            print("   - Check file permissions")
            print("   - Check file exists")
            print("   - Check file format")
            
        try:
            await database.disconnect()
        except:
            pass

if __name__ == "__main__":
    asyncio.run(test_email_generation_live())