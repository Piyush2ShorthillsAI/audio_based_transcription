#!/usr/bin/env python3
"""Test what audio formats Gemini actually supports"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

def test_gemini_formats():
    """Test Gemini's supported file formats"""
    print("🔍 TESTING GEMINI SUPPORTED FORMATS")
    print("=" * 80)
    
    try:
        # Initialize Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ GEMINI_API_KEY not found")
            return
        
        genai.configure(api_key=api_key)
        print(f"✅ Gemini configured with API key")
        
        # Check available models
        print(f"\n📋 Available Gemini Models:")
        print("-" * 40)
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(f"   📦 {model.name}")
                print(f"      Input tokens: {model.input_token_limit}")
                print(f"      Output tokens: {model.output_token_limit}")
        
        # Check what formats are available in our audio directory
        print(f"\n📁 Available Audio Files:")
        print("-" * 40)
        audio_dir = Path("uploads/audio")
        
        webm_files = list(audio_dir.glob("*.webm"))
        mp3_files = list(audio_dir.glob("*.mp3"))
        wav_files = list(audio_dir.glob("*.wav"))
        m4a_files = list(audio_dir.glob("*.m4a"))
        
        print(f"   🎵 WebM files: {len(webm_files)}")
        print(f"   🎵 MP3 files: {len(mp3_files)}")
        print(f"   🎵 WAV files: {len(wav_files)}")
        print(f"   🎵 M4A files: {len(m4a_files)}")
        
        # Test with different formats
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Test WebM file
        if webm_files:
            print(f"\n🧪 Testing WebM File:")
            print("-" * 40)
            webm_file = webm_files[0]
            print(f"   File: {webm_file.name} ({webm_file.stat().st_size} bytes)")
            
            try:
                print(f"   ⬆️  Uploading WebM...")
                uploaded_webm = genai.upload_file(path=str(webm_file))
                print(f"   📄 File ID: {uploaded_webm.name}")
                print(f"   ⏳ Initial state: {uploaded_webm.state.name}")
                
                # Wait and check final state
                import time
                wait_count = 0
                while uploaded_webm.state.name == "PROCESSING" and wait_count < 6:
                    time.sleep(5)
                    uploaded_webm = genai.get_file(name=uploaded_webm.name)
                    print(f"   ⏳ State after {(wait_count+1)*5}s: {uploaded_webm.state.name}")
                    wait_count += 1
                
                print(f"   🏁 Final WebM state: {uploaded_webm.state.name}")
                
            except Exception as e:
                print(f"   ❌ WebM failed: {str(e)}")
        
        # Test MP3 file
        if mp3_files:
            print(f"\n🧪 Testing MP3 File:")
            print("-" * 40)
            mp3_file = mp3_files[0]
            print(f"   File: {mp3_file.name} ({mp3_file.stat().st_size} bytes)")
            
            try:
                print(f"   ⬆️  Uploading MP3...")
                uploaded_mp3 = genai.upload_file(path=str(mp3_file))
                print(f"   📄 File ID: {uploaded_mp3.name}")
                print(f"   ⏳ Initial state: {uploaded_mp3.state.name}")
                
                # Wait and check final state
                import time
                wait_count = 0
                while uploaded_mp3.state.name == "PROCESSING" and wait_count < 6:
                    time.sleep(5)
                    uploaded_mp3 = genai.get_file(name=uploaded_mp3.name)
                    print(f"   ⏳ State after {(wait_count+1)*5}s: {uploaded_mp3.state.name}")
                    wait_count += 1
                
                print(f"   🏁 Final MP3 state: {uploaded_mp3.state.name}")
                
                # If MP3 works, try a quick test
                if uploaded_mp3.state.name == "ACTIVE":
                    print(f"   🤖 Testing content generation...")
                    response = model.generate_content([
                        "What can you hear in this audio? Respond in 20 words.",
                        uploaded_mp3
                    ])
                    print(f"   ✅ MP3 generated response: {response.text[:100]}...")
                
            except Exception as e:
                print(f"   ❌ MP3 failed: {str(e)}")
        
        # Provide official documentation info
        print(f"\n📚 GEMINI AUDIO FORMAT SUPPORT:")
        print("-" * 40)
        print("According to Google AI documentation, Gemini supports:")
        print("✅ MP3 - Most reliable")
        print("✅ WAV - Good support")
        print("✅ M4A - Good support")  
        print("⚠️  WebM - Limited/experimental support")
        print("⚠️  OGG - Limited support")
        
        print(f"\n💡 RECOMMENDATIONS:")
        print("-" * 40)
        print("1. 🎯 Convert WebM to MP3 for best results")
        print("2. 📱 Update frontend to record MP3 instead of WebM")
        print("3. 🔄 Add server-side conversion from WebM to MP3")
        print("4. ⚠️  Show user a warning when uploading WebM files")
        
        print(f"\n" + "=" * 80)
        print("🎯 FORMAT TESTING COMPLETED")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR DURING FORMAT TESTING!")
        print(f"🔍 Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gemini_formats()