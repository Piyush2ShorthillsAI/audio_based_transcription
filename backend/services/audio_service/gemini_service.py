import os
import time
import google.generativeai as genai
from typing import Dict, Any
from dotenv import load_dotenv
from pathlib import Path

# Get the backend directory path (where .env file is located)
backend_dir = Path(__file__).parent.parent.parent
env_path = backend_dir / '.env'

# Load environment variables from .env file with absolute path
load_dotenv(dotenv_path=env_path)

class GeminiService:
    """Simple service for Gemini AI email generation"""
    
    def __init__(self):
        """Initialize Gemini service with API key"""
        # Get API key from environment variable
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Initialize the model with gemini-2.5-pro
        self.model = genai.GenerativeModel("gemini-2.5-pro")
    
    def generate_email_from_audio_files_direct(
        self,
        relationship_audio_path: str,
        content_audio_path: str,
        recipient_name: str = "",
        recipient_email: str = "",
        relationship: str = "professional"
    ) -> Dict[str, Any]:
        """
        Generate email directly from audio files using simple Gemini approach
        """
        try:
            print(f"🎵 Processing audio files...")
            print(f"🎵 Relationship audio: {relationship_audio_path}")
            print(f"🎵 Content audio: {content_audio_path}")
            
            # Upload audio files
            print("🎵 AUDIO PROCESSING STARTED")
            print("=" * 50)
            print(f"📁 Relationship audio file: {relationship_audio_path}")
            print(f"📁 Content audio file: {content_audio_path}")
            
            print(f"⬆️ Uploading relationship audio...")
            audio_file1 = genai.upload_file(path=relationship_audio_path)
            
            print(f"⬆️ Uploading content audio...")
            audio_file2 = genai.upload_file(path=content_audio_path)
            
            # Wait for processing
            print("⏳ Waiting for audio processing...")
            while audio_file1.state.name == "PROCESSING" or audio_file2.state.name == "PROCESSING":
                print(f"File {audio_file1.name} is still {audio_file1.state.name}.")
                print(f"File {audio_file2.name} is still {audio_file2.state.name}.")
                time.sleep(10)
                audio_file1 = genai.get_file(name=audio_file1.name)
                audio_file2 = genai.get_file(name=audio_file2.name)
            
            print(f"✅ File {audio_file1.name} is {audio_file1.state.name}")
            print(f"✅ File {audio_file2.name} is {audio_file2.state.name}")
            print("🎵 AUDIO PROCESSING COMPLETED")
            print("=" * 50)
            
            # Define the prompt
            prompt = """
TASK: Generate a professional email from two audio inputs - one with relationship context, one with content details.
 
LANGUAGE SELECTION:
- Hindi/Hinglish mentioned → Use Hinglish (natural Hindi-English mix)
- Other language specified → Use that language  
- No preference/English → Use English
 
OUTPUT FORMAT:
 
ANALYSIS (in English):
Recipient: [name, title]
Relationship: [type]
Details: [key recipient info]
Purpose: [main objective]
Tone: [formality level]
Action Needed: [specific request]

EMAIL (in selected language):

Subject: [clear, specific subject]

[Appropriate greeting]

[Context paragraph if needed]

[Main message - organized logically]

[Closing with clear call-to-action]

[Professional sign-off]
 
REQUIREMENTS:
✓ Match tone to relationship (formal/business vs casual/personal)
✓ Include all key content from audio
✓ Natural language flow
✓ Clear next steps
✓ Cultural appropriateness
✓ Highlight urgent/time-sensitive items
✓ Do not use asterisks (*), separators (***), or markdown formatting
✓ Use simple text formatting only
 
Analyze both audios and generate the email.
"""
            
            # Check if files are in ACTIVE state before using
            if audio_file1.state.name != "ACTIVE":
                print(f"❌ Audio file 1 failed: {audio_file1.state.name}")
                return f"❌ Error: Audio file 1 could not be processed by Gemini. File state: {audio_file1.state.name}. This usually happens with .webm files - try uploading .mp3 files instead."
            
            if audio_file2.state.name != "ACTIVE":
                print(f"❌ Audio file 2 failed: {audio_file2.state.name}")
                return f"❌ Error: Audio file 2 could not be processed by Gemini. File state: {audio_file2.state.name}. This usually happens with .webm files - try uploading .mp3 files instead."
            
            # Generate content
            print("🤖 Sending request to Gemini 2.5 Pro...")
            try:
                response = self.model.generate_content([prompt, audio_file1, audio_file2])
                # Get the response text and return directly
                generated_content = response.text
                
            except Exception as e:
                print(f"❌ Gemini API error: {str(e)}")
                return f"❌ Error: Gemini API failed to process the audio files. Error: {str(e)}. This often happens with .webm files - try uploading .mp3 files instead."
            
            print("=" * 80)
            print("🎉 GEMINI RESPONSE RECEIVED")
            print("=" * 80)
            print(f"📊 Response Length: {len(generated_content)} characters")
            print(f"📝 Response Content:")
            print("-" * 80)
            print(generated_content)
            print("-" * 80)
            print("✅ Gemini processing completed successfully")
            print("=" * 80)
            
            return generated_content
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return f"Error generating email: {str(e)}"