#!/usr/bin/env python3
"""Test the audio service directly to find the real issue"""

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

async def test_audio_service_directly():
    """Test the audio service method directly with known recording IDs"""
    print("🔍 TESTING AUDIO SERVICE DIRECTLY")
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
        
        # Get recent recordings
        recordings_query = """
        SELECT id, user_id, contact_id, title, filename, file_path, audio_type, status, created_at
        FROM audio_recordings 
        WHERE status = 'uploaded'
        ORDER BY created_at DESC 
        LIMIT 4
        """
        
        recordings = await database.fetch_all(recordings_query)
        print(f"✅ Found {len(recordings)} uploaded recordings")
        
        if len(recordings) >= 2:
            # Use the first two recordings
            recording1 = recordings[0]
            recording2 = recordings[1]
            
            print(f"\n🎯 Testing with real recordings:")
            print(f"   Recording 1: {recording1['id']} ({recording1['audio_type']})")
            print(f"   Recording 2: {recording2['id']} ({recording2['audio_type']})")
            print(f"   User: {recording1['user_id']}")
            print(f"   Files: {recording1['file_path']} & {recording2['file_path']}")
            
            # Test the EXACT method that main.py calls
            print(f"\n🚀 Calling generate_email_from_dual_audio_direct...")
            
            result = await audio_service.generate_email_from_dual_audio_direct(
                relationship_recording_id=recording1['id'],  # Using first as relationship
                content_recording_id=recording2['id'],       # Using second as content
                user_id=recording1['user_id'],
                recipient_name="Test Recipient",
                recipient_email="test@example.com",
                relationship="professional"
            )
            
            print("✅ SUCCESS! Method completed")
            print(f"📧 Email result type: {type(result.get('email'))}")
            print(f"📧 Email length: {len(str(result.get('email', '')))}")
            print(f"📊 Analysis: {result.get('analysis', {})}")
            print(f"🔧 Processing method: {result.get('processing_method')}")
            
            # Show first part of email
            email_content = str(result.get('email', ''))
            print(f"\n📧 Email preview (first 300 chars):")
            print("-" * 50)
            print(email_content[:300] + "..." if len(email_content) > 300 else email_content)
            print("-" * 50)
            
            # This is exactly what main.py does:
            main_response = {
                "message": "Email generated successfully from direct audio processing",
                "email": result["email"],
                "analysis": result.get("analysis", {}),
                "processing_method": result["processing_method"]
            }
            
            print(f"\n📡 What main.py would return to frontend:")
            print(f"   message: {main_response['message']}")
            print(f"   email type: {type(main_response['email'])}")
            print(f"   analysis: {main_response['analysis']}")
            print(f"   processing_method: {main_response['processing_method']}")
            
        else:
            print("❌ Not enough uploaded recordings to test")
            print("💡 Upload some audio files from frontend first")
        
        await database.disconnect()
        
    except Exception as e:
        print(f"\n❌ ERROR FOUND!")
        print(f"🔍 Error type: {type(e).__name__}")
        print(f"📝 Error message: {str(e)}")
        print("\n📊 Full traceback:")
        import traceback
        traceback.print_exc()
        
        print(f"\n💡 This is likely the cause of the 500 error!")

if __name__ == "__main__":
    asyncio.run(test_audio_service_directly())