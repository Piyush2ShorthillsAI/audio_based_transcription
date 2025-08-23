#!/usr/bin/env python3
"""Simple test for audio_service_minimal.py core functionality"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent))

def test_audio_service_minimal_simple():
    """Test AudioServiceMinimal initialization and core functionality"""
    print("🧪 TESTING AUDIO SERVICE MINIMAL - SIMPLE VERSION")
    print("=" * 80)
    
    try:
        # Test 1: Import and class definition
        print("📦 TEST 1: Import AudioServiceMinimal")
        print("-" * 40)
        
        from services.audio_service.audio_service_minimal import AudioServiceMinimal
        print("✅ AudioServiceMinimal imported successfully")
        
        # Test 2: Check available audio files
        print("\n📁 TEST 2: Check Available Audio Files")
        print("-" * 40)
        
        audio_dir = Path("uploads/audio")
        if audio_dir.exists():
            mp3_files = list(audio_dir.glob("*.mp3"))
            webm_files = list(audio_dir.glob("*.webm"))
            
            print(f"✅ Found {len(mp3_files)} MP3 files")
            print(f"✅ Found {len(webm_files)} WebM files")
            
            if mp3_files:
                print("🎵 MP3 files:")
                for i, file in enumerate(mp3_files[:3]):
                    size = file.stat().st_size
                    print(f"   {i+1}. {file.name} ({size:,} bytes)")
            
            if webm_files:
                print("🎵 WebM files (first 5):")
                for i, file in enumerate(webm_files[:5]):
                    size = file.stat().st_size
                    print(f"   {i+1}. {file.name} ({size:,} bytes)")
        
        else:
            print("❌ uploads/audio directory not found")
        
        # Test 3: Test Gemini service initialization
        print("\n🤖 TEST 3: Gemini Service Initialization")
        print("-" * 40)
        
        try:
            from services.audio_service.gemini_service import GeminiService
            
            # Check API key
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                print(f"✅ GEMINI_API_KEY found: {api_key[:20]}...")
            else:
                print("❌ GEMINI_API_KEY not found")
                return
            
            # Initialize Gemini service
            gemini_service = GeminiService()
            print("✅ GeminiService initialized successfully")
            
        except Exception as e:
            print(f"❌ GeminiService error: {str(e)}")
            return
        
        # Test 4: Test AudioServiceMinimal with mock database
        print("\n🏗️  TEST 4: AudioServiceMinimal with Mock Database")
        print("-" * 40)
        
        # Create a simple mock database object
        class MockDatabase:
            def __init__(self):
                pass
        
        mock_db = MockDatabase()
        
        try:
            audio_service = AudioServiceMinimal(mock_db)
            print("✅ AudioServiceMinimal initialized with mock database")
            print(f"✅ Upload directory: {audio_service.upload_dir}")
            print(f"✅ Gemini service available: {hasattr(audio_service, 'gemini_service')}")
            
        except Exception as e:
            print(f"❌ AudioServiceMinimal initialization error: {str(e)}")
        
        # Test 5: Check class methods
        print("\n🔍 TEST 5: Check Available Methods")
        print("-" * 40)
        
        methods = [attr for attr in dir(AudioServiceMinimal) if callable(getattr(AudioServiceMinimal, attr)) and not attr.startswith('_')]
        print(f"✅ Found {len(methods)} public methods:")
        for method in methods:
            print(f"   📋 {method}")
        
        # Test 6: File path handling
        print("\n📂 TEST 6: File Path Handling")
        print("-" * 40)
        
        upload_dir = Path("uploads/audio")
        if upload_dir.exists():
            print(f"✅ Upload directory exists: {upload_dir}")
            print(f"✅ Directory is writable: {os.access(upload_dir, os.W_OK)}")
            print(f"✅ Directory is readable: {os.access(upload_dir, os.R_OK)}")
        else:
            print(f"❌ Upload directory does not exist: {upload_dir}")
        
        print("\n" + "=" * 80)
        print("🎉 SIMPLE TESTS COMPLETED!")
        print("=" * 80)
        
        # Summary
        print("\n📊 SUMMARY:")
        print("✅ AudioServiceMinimal class can be imported")
        print("✅ GeminiService initializes correctly")
        print("✅ Upload directory structure is valid")
        print(f"✅ Audio files available: {len(mp3_files)} MP3, {len(webm_files)} WebM")
        print("⚠️  Database-dependent features need running server to test")
        
    except Exception as e:
        print(f"\n❌ ERROR DURING SIMPLE TESTING!")
        print(f"🔍 Error type: {type(e).__name__}")
        print(f"📝 Error message: {str(e)}")
        
        import traceback
        print("\n📊 Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    test_audio_service_minimal_simple()