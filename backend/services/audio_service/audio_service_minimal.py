import os
import uuid
import aiofiles
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from ..db_service.database import database
from .gemini_service import GeminiService


class AudioServiceMinimal:
    """Minimal Audio Service - ONLY for direct Gemini processing (no transcription)"""
    
    def __init__(self, database, upload_dir: str = "uploads/audio"):
        """Initialize minimal audio service"""
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Only initialize Gemini service
        self.gemini_service = GeminiService()
        
        # Store database reference
        self.database = database
    
    async def save_audio_file(
        self,
        audio_file,
        user_id: str,
        title: str,
        contact_id: Optional[str] = None,
        audio_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Save uploaded audio file - ALWAYS converts to MP3 format only"""
        try:
            # Generate unique filename with original extension for temporary storage
            file_extension = audio_file.filename.split('.')[-1] if '.' in audio_file.filename else 'webm'
            temp_filename = f"{uuid.uuid4()}.{file_extension}"
            temp_file_path = self.upload_dir / temp_filename
            
            # Save temporary file to disk
            async with aiofiles.open(temp_file_path, 'wb') as f:
                content = await audio_file.read()
                await f.write(content)
            
            print(f"📁 Uploaded temporary file: {temp_filename}")
            
            # Convert to MP3 format (this will handle the conversion or return as-is if already MP3)
            mp3_file_path = await self._ensure_mp3_format(str(temp_file_path), recording_id=None)
            
            # Get final MP3 file details
            import os
            from pathlib import Path
            mp3_path_obj = Path(mp3_file_path)
            file_size = os.path.getsize(mp3_file_path) if mp3_path_obj.exists() else len(content)
            final_filename = mp3_path_obj.name
            
            # Delete original file if it was converted (different from MP3 output)
            if str(temp_file_path) != mp3_file_path:
                try:
                    temp_file_path.unlink()  # Delete original file
                    print(f"🗑️ Deleted temporary file: {temp_filename}")
                except Exception as e:
                    print(f"⚠️ Could not delete temporary file: {e}")
            
            print(f"💾 Final MP3 file: {final_filename} ({file_size} bytes)")
            
            # Create database record in appropriate table based on audio_type
            recording_id = str(uuid.uuid4())
            
            if audio_type == "action":
                # Save to action_recordings table
                query = """
                INSERT INTO action_recordings (
                    id, user_id, contact_id, title, filename, file_path, file_size,
                    status, format, created_at, updated_at
                ) VALUES (
                    :id, :user_id, :contact_id, :title, :filename, :file_path, :file_size,
                    :status, :format, NOW(), NOW()
                ) RETURNING *
                """
                
                result = await self.database.fetch_one(query, {
                    "id": recording_id,
                    "user_id": user_id,
                    "contact_id": contact_id,
                    "title": title,
                    "filename": final_filename,
                    "file_path": mp3_file_path,
                    "file_size": file_size,
                    "status": "uploaded",
                    "format": "audio/mp3"
                })
                
            elif audio_type == "context":
                # For context recordings, we need an action_recording_id
                # This should be provided or we need to find the most recent action recording
                if not contact_id:
                    raise Exception("contact_id is required for context recordings")
                
                # Find the most recent action recording for this user and contact
                action_query = """
                SELECT id FROM action_recordings 
                WHERE user_id = :user_id AND contact_id = :contact_id 
                ORDER BY created_at DESC 
                LIMIT 1
                """
                action_result = await self.database.fetch_one(action_query, {
                    "user_id": user_id,
                    "contact_id": contact_id
                })
                
                if not action_result:
                    raise Exception("No action recording found. Context recordings must be linked to an action recording.")
                
                action_recording_id = action_result["id"]
                
                # Save to context_recordings table
                query = """
                INSERT INTO context_recordings (
                    id, user_id, contact_id, action_recording_id, title, filename, file_path, file_size,
                    status, format, created_at, updated_at
                ) VALUES (
                    :id, :user_id, :contact_id, :action_recording_id, :title, :filename, :file_path, :file_size,
                    :status, :format, NOW(), NOW()
                ) RETURNING *
                """
                
                result = await self.database.fetch_one(query, {
                    "id": recording_id,
                    "user_id": user_id,
                    "contact_id": contact_id,
                    "action_recording_id": action_recording_id,
                    "title": title,
                    "filename": final_filename,
                    "file_path": mp3_file_path,
                    "file_size": file_size,
                    "status": "uploaded",
                    "format": "audio/mp3"
                })
            else:
                raise Exception(f"Invalid audio_type: {audio_type}. Must be 'action' or 'context'")
            
            return {
                "recording_id": recording_id,
                "filename": final_filename,
                "file_path": mp3_file_path,
                "file_size": file_size,
                "duration": None,  # Not extracted in minimal mode
                "status": "uploaded",
                "format": "audio/mp3",
                "message": "Audio file saved as MP3 successfully"
            }
            
        except Exception as e:
            print(f"Error saving audio file: {str(e)}")
            raise Exception(f"Failed to save audio file: {str(e)}")
    
    async def generate_email_from_dual_audio_direct(
        self,
        relationship_recording_id: str,
        content_recording_id: str,
        user_id: str,
        recipient_name: str = "",
        recipient_email: str = "",
        relationship: str = "professional"
    ) -> Dict[str, Any]:
        """Generate email directly from two audio files - SIMPLIFIED"""
        try:
            print(f"🔍 Looking for recordings: {relationship_recording_id}, {content_recording_id}")
            
            # Get both recordings from database
            # Convert string IDs to UUID objects for database query
            import uuid as uuid_lib
            try:
                relationship_uuid = uuid_lib.UUID(relationship_recording_id) if isinstance(relationship_recording_id, str) else relationship_recording_id
                content_uuid = uuid_lib.UUID(content_recording_id) if isinstance(content_recording_id, str) else content_recording_id
                user_uuid = uuid_lib.UUID(user_id) if isinstance(user_id, str) else user_id
            except ValueError as e:
                raise Exception(f"Invalid UUID format: {str(e)}")
            
            # Query both action_recordings and context_recordings tables
            action_query = """
            SELECT id, file_path, filename, 'action' as recording_type FROM action_recordings 
            WHERE id IN (:relationship_id, :content_id) AND user_id = :user_id
            """
            
            context_query = """
            SELECT id, file_path, filename, 'context' as recording_type FROM context_recordings 
            WHERE id IN (:relationship_id, :content_id) AND user_id = :user_id
            """
            
            # Get recordings from both tables
            action_recordings = await self.database.fetch_all(action_query, {
                "relationship_id": relationship_uuid,
                "content_id": content_uuid,
                "user_id": user_uuid
            })
            
            context_recordings = await self.database.fetch_all(context_query, {
                "relationship_id": relationship_uuid,
                "content_id": content_uuid,
                "user_id": user_uuid
            })
            
            # Combine results
            recordings = list(action_recordings) + list(context_recordings)
            
            print(f"📊 Database query returned {len(recordings)} recording(s)")
            for rec in recordings:
                print(f"   📄 Found: {rec['id']} -> {rec['filename']} ({rec['file_path']}) [type: {rec['recording_type']}]")
            
            if len(recordings) == 0:
                # Check if recordings exist in either table for debugging
                debug_action_query = """
                SELECT id, user_id FROM action_recordings 
                WHERE id IN (:relationship_id, :content_id)
                """
                debug_context_query = """
                SELECT id, user_id FROM context_recordings 
                WHERE id IN (:relationship_id, :content_id)
                """
                
                debug_action_recordings = await self.database.fetch_all(debug_action_query, {
                    "relationship_id": relationship_uuid,
                    "content_id": content_uuid
                })
                
                debug_context_recordings = await self.database.fetch_all(debug_context_query, {
                    "relationship_id": relationship_uuid,
                    "content_id": content_uuid
                })
                
                debug_recordings = list(debug_action_recordings) + list(debug_context_recordings)
                
                if debug_recordings:
                    different_users = [str(r['user_id']) for r in debug_recordings]
                    print(f"⚠️  Found recordings but for different user: {different_users}")
                    raise Exception(f"No recordings found for user {user_id}. Recordings exist but belong to different user(s): {different_users}")
                else:
                    raise Exception(f"No recordings found with IDs {relationship_recording_id} and {content_recording_id}")
                    
            elif len(recordings) == 1:
                found_id_str = str(recordings[0]["id"])
                relationship_id_str = str(relationship_recording_id)
                content_id_str = str(content_recording_id)
                
                missing_id = content_recording_id if found_id_str == relationship_id_str else relationship_recording_id
                missing_type = "content" if found_id_str == relationship_id_str else "relationship"
                raise Exception(f"Missing {missing_type} recording with ID: {missing_id}")
                
            elif len(recordings) != 2:
                raise Exception(f"Expected 2 recordings, found {len(recordings)}")
            
            # Get file paths and validate files exist
            relationship_audio_path = None
            content_audio_path = None
            
            for recording in recordings:
                rec_id = recording["id"]
                file_path = recording["file_path"]
                print(f"   🔍 Processing recording {rec_id}")
                print(f"      📁 File path: {file_path}")
                
                if not file_path:
                    print(f"      ❌ No file path in database")
                    raise Exception(f"Recording {rec_id} has no file path in database")
                
                # Check if file actually exists
                print(f"      🔍 Checking if file exists...")
                file_exists = os.path.exists(file_path)
                print(f"      {'✅' if file_exists else '❌'} File exists: {file_exists}")
                
                if not file_exists:
                    print(f"      ❌ File not found on disk: {file_path}")
                    raise Exception(f"Audio file not found: {file_path} for recording {rec_id}")
                
                print(f"      🔍 Checking ID mapping...")
                print(f"         Expected relationship: '{relationship_recording_id}'")
                print(f"         Expected content: '{content_recording_id}'")
                print(f"         Current record: '{rec_id}'")
                
                # Convert ALL to strings for comparison (database returns UUID objects, params are strings)
                rec_id_str = str(rec_id)
                relationship_id_str = str(relationship_recording_id)
                content_id_str = str(content_recording_id)
                
                if rec_id_str == relationship_id_str:
                    relationship_audio_path = file_path
                    print(f"      ✅ Mapped as RELATIONSHIP audio: {os.path.basename(file_path)}")
                elif rec_id_str == content_id_str:
                    content_audio_path = file_path
                    print(f"      ✅ Mapped as CONTENT audio: {os.path.basename(file_path)}")
                else:
                    print(f"      ⚠️  ID doesn't match either expected ID")
                print()
            
            print(f"📋 Final mapping results:")
            print(f"   📱 Relationship path: {relationship_audio_path}")
            print(f"   📱 Content path: {content_audio_path}")
            
            if not relationship_audio_path or not content_audio_path:
                raise Exception(f"Could not map recording IDs to file paths. Relationship: {relationship_audio_path}, Content: {content_audio_path}")
            
            # Ensure BOTH audio files are in MP3 format for Gemini compatibility
            print(f"🔄 Converting both audio files to MP3 format...")
            relationship_audio_path = await self._ensure_mp3_format(relationship_audio_path, relationship_recording_id)
            content_audio_path = await self._ensure_mp3_format(content_audio_path, content_recording_id)
            
            from pathlib import Path
            print(f"🎵 Using MP3 files for Gemini:")
            print(f"   📁 Relationship: {Path(relationship_audio_path).name}")
            print(f"   📁 Content: {Path(content_audio_path).name}")
            
            # Generate email using Gemini
            import asyncio
            email_result = await asyncio.to_thread(
                self.gemini_service.generate_email_from_audio_files_direct,
                relationship_audio_path=relationship_audio_path,
                content_audio_path=content_audio_path,
                recipient_name=recipient_name,
                recipient_email=recipient_email,
                relationship=relationship
            )
            
            return {
                "email": email_result,  # Send raw Gemini response directly
                "analysis": {"text": "Generated by Gemini 2.5 Pro"}, 
                "processing_method": "direct_audio_to_gemini"
            }
            
        except Exception as e:
            raise Exception(f"Failed to process audio: {str(e)}")
    
    async def _ensure_mp3_format(self, file_path: str, recording_id: str = None) -> str:
        """Ensure audio file is in MP3 format - convert if necessary and update database"""
        from pathlib import Path
        import subprocess
        import os
        
        file_path_obj = Path(file_path)
        
        # If already MP3, return as-is
        if file_path_obj.suffix.lower() == '.mp3':
            print(f"   ✅ Already MP3: {file_path_obj.name}")
            return file_path
        
        # If WebM or other format, convert to MP3
        if file_path_obj.suffix.lower() in ['.webm', '.wav', '.m4a', '.ogg']:
            mp3_path = str(file_path_obj.with_suffix('.mp3'))
            
            # Check if MP3 already exists
            if Path(mp3_path).exists():
                print(f"   ♻️  Using existing MP3: {Path(mp3_path).name}")
                
                # Update database if recording_id is provided
                if recording_id:
                    await self._update_database_for_mp3(recording_id, mp3_path)
                
                return mp3_path
            
            # Convert to MP3
            try:
                print(f"   🔄 Converting {file_path_obj.name} → MP3...")
                
                cmd = [
                    'ffmpeg',
                    '-i', str(file_path_obj),    # Input file
                    '-acodec', 'mp3',            # MP3 codec
                    '-ab', '128k',               # Bitrate 128kbps
                    '-ar', '44100',              # Sample rate 44.1kHz
                    '-y',                        # Overwrite output file
                    mp3_path                     # Output MP3 file
                ]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                print(f"   ✅ Converted to MP3: {Path(mp3_path).name}")
                
                # Update database if recording_id is provided
                if recording_id:
                    await self._update_database_for_mp3(recording_id, mp3_path)
                
                return mp3_path
                
            except subprocess.CalledProcessError as e:
                print(f"   ⚠️  FFmpeg conversion failed: {e.stderr}")
                print(f"   📄 Using original file: {file_path_obj.name}")
                return file_path
            except FileNotFoundError:
                print(f"   ⚠️  FFmpeg not installed - using original file")
                return file_path
        
        # For other formats, return as-is
        print(f"   ⚪ Unknown format: {file_path_obj.name}")
        return file_path

    async def _update_database_for_mp3(self, recording_id: str, mp3_path: str):
        """Update database record to reflect MP3 conversion - works with both action and context recordings"""
        try:
            from pathlib import Path
            import os
            
            mp3_file = Path(mp3_path)
            file_size = os.path.getsize(mp3_path) if mp3_file.exists() else 0
            
            # Try to update in action_recordings first
            action_update_query = """
            UPDATE action_recordings 
            SET file_path = :file_path,
                filename = :filename,
                format = :format,
                file_size = :file_size,
                updated_at = NOW()
            WHERE id = :recording_id
            """
            
            action_result = await self.database.execute(action_update_query, {
                "file_path": mp3_path,
                "filename": mp3_file.name,
                "format": "audio/mp3",
                "file_size": file_size,
                "recording_id": recording_id
            })
            
            # If no rows affected in action_recordings, try context_recordings
            if action_result == 0:
                context_update_query = """
                UPDATE context_recordings 
                SET file_path = :file_path,
                    filename = :filename,
                    format = :format,
                    file_size = :file_size,
                    updated_at = NOW()
                WHERE id = :recording_id
                """
                
                context_result = await self.database.execute(context_update_query, {
                    "file_path": mp3_path,
                    "filename": mp3_file.name,
                    "format": "audio/mp3",
                    "file_size": file_size,
                    "recording_id": recording_id
                })
                
                if context_result == 0:
                    print(f"   ⚠️  Recording ID {recording_id} not found in either table")
                    return
                else:
                    print(f"   💾 Context recording updated: {mp3_file.name} (size: {file_size} bytes)")
            else:
                print(f"   💾 Action recording updated: {mp3_file.name} (size: {file_size} bytes)")
            
        except Exception as e:
            print(f"   ⚠️  Database update failed: {str(e)}")
            # Don't fail the conversion, just log the error

    async def get_user_recordings(self, user_id: str):
        """Get all audio recordings for a specific user from both action and context tables"""
        
        action_query = """
        SELECT id, user_id, contact_id, title, filename, file_path, 
               file_size, 'action' as audio_type, status, format, duration, created_at
        FROM action_recordings 
        WHERE user_id = :user_id 
        ORDER BY created_at DESC
        """
        
        context_query = """
        SELECT id, user_id, contact_id, title, filename, file_path, 
               file_size, 'context' as audio_type, status, format, duration, created_at
        FROM context_recordings 
        WHERE user_id = :user_id 
        ORDER BY created_at DESC
        """
        
        try:
            # Get recordings from both tables
            action_recordings = await self.database.fetch_all(action_query, {
                "user_id": user_id
            })
            
            context_recordings = await self.database.fetch_all(context_query, {
                "user_id": user_id
            })
            
            # Combine and sort by created_at
            all_recordings = list(action_recordings) + list(context_recordings)
            
            if not all_recordings:
                return []
            
            # Convert to dict format and sort by creation time (newest first)
            recordings_dict = [dict(recording) for recording in all_recordings]
            recordings_dict.sort(key=lambda x: x['created_at'], reverse=True)
            
            return recordings_dict
            
        except Exception as e:
            print(f"❌ Error getting user recordings: {e}")
            return []