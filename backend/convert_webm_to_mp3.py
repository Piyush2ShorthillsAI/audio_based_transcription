#!/usr/bin/env python3
"""Convert WebM files to MP3 for Gemini compatibility"""

import subprocess
import os
from pathlib import Path
import asyncio

def convert_webm_to_mp3(webm_path: str, mp3_path: str = None) -> str:
    """
    Convert WebM audio file to MP3 using ffmpeg
    
    Args:
        webm_path: Path to input WebM file
        mp3_path: Optional output MP3 path (auto-generated if None)
    
    Returns:
        Path to converted MP3 file
    """
    webm_file = Path(webm_path)
    
    if not webm_file.exists():
        raise FileNotFoundError(f"WebM file not found: {webm_path}")
    
    # Generate MP3 path if not provided
    if mp3_path is None:
        mp3_path = str(webm_file.with_suffix('.mp3'))
    
    mp3_file = Path(mp3_path)
    
    # Check if already converted
    if mp3_file.exists():
        print(f"✅ MP3 already exists: {mp3_path}")
        return str(mp3_file)
    
    # Convert using ffmpeg
    try:
        print(f"🔄 Converting {webm_file.name} to MP3...")
        
        cmd = [
            'ffmpeg',
            '-i', str(webm_file),     # Input WebM file
            '-acodec', 'mp3',         # MP3 codec
            '-ab', '128k',            # Bitrate 128kbps
            '-ar', '44100',           # Sample rate 44.1kHz
            '-y',                     # Overwrite output file
            str(mp3_file)             # Output MP3 file
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        print(f"✅ Converted successfully: {mp3_file.name}")
        print(f"   Original: {webm_file.stat().st_size} bytes")
        print(f"   Converted: {mp3_file.stat().st_size} bytes")
        
        return str(mp3_file)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg conversion failed: {e}")
        print(f"   Error output: {e.stderr}")
        raise Exception(f"Failed to convert WebM to MP3: {e.stderr}")
    
    except FileNotFoundError:
        raise Exception("FFmpeg not installed. Install with: sudo apt install ffmpeg")

async def convert_all_webm_files():
    """Convert all WebM files in uploads/audio to MP3"""
    audio_dir = Path("uploads/audio")
    
    if not audio_dir.exists():
        print("❌ Audio directory not found: uploads/audio")
        return
    
    webm_files = list(audio_dir.glob("*.webm"))
    print(f"📁 Found {len(webm_files)} WebM files to convert")
    
    converted_count = 0
    failed_count = 0
    
    for webm_file in webm_files:
        try:
            mp3_path = convert_webm_to_mp3(str(webm_file))
            converted_count += 1
            
        except Exception as e:
            print(f"❌ Failed to convert {webm_file.name}: {str(e)}")
            failed_count += 1
    
    print(f"\n📊 CONVERSION SUMMARY:")
    print(f"   ✅ Converted: {converted_count}")
    print(f"   ❌ Failed: {failed_count}")
    print(f"   📁 Total WebM files: {len(webm_files)}")

if __name__ == "__main__":
    # Test conversion
    asyncio.run(convert_all_webm_files())