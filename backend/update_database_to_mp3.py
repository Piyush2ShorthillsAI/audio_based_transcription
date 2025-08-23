#!/usr/bin/env python3
"""Update database records from WebM to MP3 format"""

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

async def update_database_to_mp3():
    """Update all WebM records in database to MP3 format"""
    print("🔄 UPDATING DATABASE RECORDS TO MP3 FORMAT")
    print("=" * 80)
    
    try:
        from services.db_service.database import database
        
        # Connect to database
        await database.connect()
        print("✅ Database connected")
        
        # Step 1: Find all WebM recordings
        print(f"\n📋 Step 1: Find WebM Records")
        print("-" * 40)
        
        webm_query = """
        SELECT id, filename, file_path, format, audio_type, user_id, created_at
        FROM audio_recordings 
        WHERE file_path LIKE '%.webm' OR format LIKE '%webm%'
        ORDER BY created_at DESC
        """
        
        webm_records = await database.fetch_all(webm_query)
        print(f"📁 Found {len(webm_records)} WebM records in database")
        
        if len(webm_records) == 0:
            print("✅ No WebM records found - database is already updated!")
            return
        
        # Step 2: Check which MP3 files exist on disk
        print(f"\n📁 Step 2: Check MP3 Files on Disk")
        print("-" * 40)
        
        updates_needed = []
        
        for record in webm_records:
            webm_path = Path(record['file_path'])
            mp3_path = webm_path.with_suffix('.mp3')
            
            if mp3_path.exists():
                updates_needed.append({
                    'id': record['id'],
                    'old_path': str(webm_path),
                    'new_path': str(mp3_path),
                    'old_format': record['format'],
                    'audio_type': record['audio_type'],
                    'mp3_size': mp3_path.stat().st_size
                })
                print(f"   ✅ {webm_path.name} → {mp3_path.name}")
            else:
                print(f"   ❌ Missing MP3: {mp3_path.name}")
        
        print(f"\n📊 Found {len(updates_needed)} records ready for MP3 update")
        
        if len(updates_needed) == 0:
            print("⚠️  No MP3 files found on disk. Run WebM to MP3 conversion first!")
            return
        
        # Step 3: Update database records
        print(f"\n🔄 Step 3: Update Database Records")
        print("-" * 40)
        
        success_count = 0
        failed_count = 0
        
        for update in updates_needed:
            try:
                # Determine new format
                new_format = 'audio/mp3'
                
                # Determine new filename
                old_filename = Path(update['old_path']).name
                new_filename = old_filename.replace('.webm', '.mp3')
                
                # Update query
                update_query = """
                UPDATE audio_recordings 
                SET file_path = :new_path,
                    filename = :new_filename,
                    format = :new_format,
                    file_size = :new_size,
                    updated_at = NOW()
                WHERE id = :record_id
                """
                
                await database.execute(update_query, {
                    'record_id': update['id'],
                    'new_path': update['new_path'],
                    'new_filename': new_filename,
                    'new_format': new_format,
                    'new_size': update['mp3_size']
                })
                
                print(f"   ✅ Updated: {old_filename} → {new_filename}")
                success_count += 1
                
            except Exception as e:
                print(f"   ❌ Failed to update {update['id']}: {str(e)}")
                failed_count += 1
        
        # Step 4: Verify updates
        print(f"\n✅ Step 4: Verification")
        print("-" * 40)
        
        # Check updated records
        mp3_query = """
        SELECT COUNT(*) as mp3_count FROM audio_recordings 
        WHERE file_path LIKE '%.mp3' OR format LIKE '%mp3%'
        """
        
        remaining_webm_query = """
        SELECT COUNT(*) as webm_count FROM audio_recordings 
        WHERE file_path LIKE '%.webm' OR format LIKE '%webm%'
        """
        
        mp3_result = await database.fetch_one(mp3_query)
        webm_result = await database.fetch_one(remaining_webm_query)
        
        print(f"📊 Database now has:")
        print(f"   🎵 MP3 records: {mp3_result['mp3_count']}")
        print(f"   🎵 WebM records remaining: {webm_result['webm_count']}")
        
        print(f"\n📈 UPDATE SUMMARY:")
        print(f"   ✅ Successfully updated: {success_count}")
        print(f"   ❌ Failed updates: {failed_count}")
        print(f"   📁 Total records processed: {len(updates_needed)}")
        
        # Show sample of updated records
        if success_count > 0:
            print(f"\n📋 Sample Updated Records:")
            print("-" * 40)
            
            sample_query = """
            SELECT filename, format, audio_type, file_size 
            FROM audio_recordings 
            WHERE format = 'audio/mp3'
            ORDER BY updated_at DESC 
            LIMIT 5
            """
            
            samples = await database.fetch_all(sample_query)
            for i, sample in enumerate(samples, 1):
                size_kb = sample['file_size'] // 1024
                print(f"   {i}. {sample['filename']} ({sample['format']}, {sample['audio_type']}, {size_kb}KB)")
        
        await database.disconnect()
        
        print(f"\n" + "=" * 80)
        print("🎉 DATABASE UPDATE COMPLETED!")
        print("=" * 80)
        
        if success_count > 0:
            print("✅ Your database now stores MP3 format records!")
            print("✅ Email generation will use MP3 file paths directly!")
            print("✅ Better Gemini compatibility achieved!")
        
    except Exception as e:
        print(f"\n❌ ERROR DURING DATABASE UPDATE!")
        print(f"🔍 Error type: {type(e).__name__}")
        print(f"📝 Error message: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(update_database_to_mp3())