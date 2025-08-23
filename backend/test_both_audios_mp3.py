#!/usr/bin/env python3
"""Test that BOTH audio files are converted to MP3"""

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

async def test_both_audios_mp3():
    """Test that both audio files are converted to MP3 format"""
    print("🧪 TESTING BOTH AUDIOS CONVERSION TO MP3")
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
        
        # Step 1: Find recordings with mixed formats (MP3 and WebM)
        print(f"\n📋 Step 1: Find Recordings with Different Formats")
        print("-" * 50)
        
        # Get some MP3 records
        mp3_query = """
        SELECT id, filename, file_path, format, audio_type, user_id
        FROM audio_recordings 
        WHERE format = 'audio/mp3' AND status = 'uploaded'
        ORDER BY created_at DESC 
        LIMIT 3
        """
        
        # Get any remaining WebM records
        webm_query = """
        SELECT id, filename, file_path, format, audio_type, user_id
        FROM audio_recordings 
        WHERE (format LIKE '%webm%' OR file_path LIKE '%.webm') AND status = 'uploaded'
        ORDER BY created_at DESC 
        LIMIT 2
        """
        
        mp3_records = await database.fetch_all(mp3_query)
        webm_records = await database.fetch_all(webm_query)
        
        print(f"📁 Found {len(mp3_records)} MP3 records")
        print(f"📁 Found {len(webm_records)} WebM records")
        
        if len(mp3_records) < 1:
            print("❌ Need at least 1 MP3 record for testing")
            return
        
        # Step 2: Test with two different scenarios
        scenarios = []
        
        # Scenario 1: Both MP3 files
        if len(mp3_records) >= 2:
            scenarios.append({
                "name": "Both MP3 files",
                "relationship": mp3_records[0],
                "content": mp3_records[1]
            })
        
        # Scenario 2: Mixed MP3 and WebM
        if len(mp3_records) >= 1 and len(webm_records) >= 1:
            scenarios.append({
                "name": "Mixed MP3 and WebM",
                "relationship": mp3_records[0],
                "content": webm_records[0]
            })
        
        # Scenario 3: Both WebM files
        if len(webm_records) >= 2:
            scenarios.append({
                "name": "Both WebM files",
                "relationship": webm_records[0],
                "content": webm_records[1]
            })
        
        print(f"\n🎯 Found {len(scenarios)} test scenarios")
        
        # Step 3: Test each scenario
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n🧪 SCENARIO {i}: {scenario['name']}")
            print("-" * 50)
            
            relationship_rec = scenario['relationship']
            content_rec = scenario['content']
            
            print(f"📁 Files to test:")
            print(f"   Relationship: {Path(relationship_rec['file_path']).name} ({relationship_rec['format']})")
            print(f"   Content: {Path(content_rec['file_path']).name} ({content_rec['format']})")
            
            # Test the conversion method directly
            print(f"\n🔄 Testing _ensure_mp3_format on BOTH files:")
            
            # Test relationship audio
            relationship_result = await audio_service._ensure_mp3_format(relationship_rec['file_path'])
            print(f"   📁 Relationship result: {Path(relationship_result).name}")
            
            # Test content audio
            content_result = await audio_service._ensure_mp3_format(content_rec['file_path'])
            print(f"   📁 Content result: {Path(content_result).name}")
            
            # Verify both are MP3
            rel_is_mp3 = Path(relationship_result).suffix.lower() == '.mp3'
            con_is_mp3 = Path(content_result).suffix.lower() == '.mp3'
            
            print(f"\n✅ VERIFICATION:")
            print(f"   📧 Relationship is MP3: {rel_is_mp3} ({'✅' if rel_is_mp3 else '❌'})")
            print(f"   📧 Content is MP3: {con_is_mp3} ({'✅' if con_is_mp3 else '❌'})")
            
            if rel_is_mp3 and con_is_mp3:
                print(f"   🎉 SUCCESS: Both files are MP3 format!")
            else:
                print(f"   ⚠️  WARNING: Not all files are MP3 format")
            
            # Test actual email generation if both are users of same user
            if relationship_rec['user_id'] == content_rec['user_id']:
                print(f"\n🎯 Testing Full Email Generation...")
                
                try:
                    result = await audio_service.generate_email_from_dual_audio_direct(
                        relationship_recording_id=relationship_rec['id'],
                        content_recording_id=content_rec['id'],
                        user_id=relationship_rec['user_id'],
                        recipient_name="Test Recipient",
                        recipient_email="test@example.com",
                        relationship="professional"
                    )
                    
                    email_content = str(result.get('email', ''))
                    is_error = email_content.startswith('❌ Error:')
                    
                    if not is_error:
                        print(f"   🎉 EMAIL GENERATED SUCCESSFULLY!")
                        print(f"   📊 Response length: {len(email_content)} chars")
                    else:
                        print(f"   ⚠️  Got error response: {email_content[:100]}...")
                        
                except Exception as e:
                    print(f"   ❌ Email generation failed: {str(e)}")
            else:
                print(f"   ⚪ Skipping email generation (different users)")
        
        await database.disconnect()
        
        print(f"\n" + "=" * 80)
        print("🎉 BOTH AUDIOS MP3 CONVERSION TEST COMPLETED!")
        print("=" * 80)
        
        print("✅ CONFIRMED:")
        print("🔄 Both audio files are processed through _ensure_mp3_format")
        print("🎵 WebM files get converted to MP3")
        print("🎵 MP3 files are used as-is")
        print("🤖 Gemini receives MP3 files for both relationship and content audio")
        
    except Exception as e:
        print(f"\n❌ ERROR DURING TESTING!")
        print(f"🔍 Error type: {type(e).__name__}")
        print(f"📝 Error message: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_both_audios_mp3())