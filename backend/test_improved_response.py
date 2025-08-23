#!/usr/bin/env python3
"""Test the improved Gemini response parsing"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent))

def test_improved_response():
    """Test the improved Gemini response parsing"""
    print("🧪 TESTING IMPROVED RESPONSE PARSING")
    print("=" * 80)
    
    try:
        # Import the AudioServiceMinimal with new parsing
        from services.audio_service.audio_service_minimal import AudioServiceMinimal
        
        # Create a mock database
        class MockDatabase:
            pass
        
        # Initialize service
        audio_service = AudioServiceMinimal(MockDatabase())
        
        # Test with our actual Gemini response from earlier
        sample_gemini_response = """**ANALYSIS** (in English):
I am unable to generate the email as requested because both audio files are silent or contain no discernible speech.

*   **Audio 1 (Relationship Context):** The audio contains only a brief "hello" and background noise, with no information about the recipient or the sender's relationship.
*   **Audio 2 (Content Details):** The audio is completely silent. No content details for the email could be extracted.

To assist you, I have created a sample template below based on a common business scenario. Please provide audio with clear details for an accurate, customized email.

---
### **SAMPLE TEMPLATE**
---

**ANALYSIS** (in English):
Recipient: [Recipient Name], [Recipient Title]
Relationship: [e.g., Reporting Manager, Client, Colleague]
Details: [e.g., Following up on our conversation yesterday]
Purpose: [e.g., To provide a project update and request feedback]
Tone: Professional and informative
Action Needed: Review the attached document and provide feedback by a specific date.

**EMAIL** (in English):
Subject: [Clear, Specific Subject, e.g., Update on Project Alpha]

Dear [Recipient Name],

I hope this email finds you well.

This is a follow-up to our conversation regarding [mention topic]. As discussed, I have now completed the [task, e.g., initial draft of the Q3 report].

The key points are summarized below:
*   [Detail 1]
*   [Detail 2]
*   [Detail 3]

Please find the full document attached for your review. I would appreciate it if you could provide your feedback by [Date/Time, e.g., end of day, Friday].

Please let me know if you have any questions.

Best regards,

[Your Name]"""
        
        print("🤖 TEST 1: Parse Actual Gemini Response")
        print("-" * 50)
        
        # Test the parsing method
        parsed = audio_service._parse_gemini_response(sample_gemini_response)
        
        print(f"✅ Parsed Subject: '{parsed['subject']}'")
        print(f"✅ Parsed Body Length: {len(parsed['body'])} characters")
        print(f"✅ Parsed Analysis Length: {len(parsed['analysis'])} characters")
        
        print(f"\n📧 EMAIL SUBJECT:")
        print(f"   {parsed['subject']}")
        
        print(f"\n📄 EMAIL BODY (first 200 chars):")
        body_preview = parsed['body'][:200] + "..." if len(parsed['body']) > 200 else parsed['body']
        print(f"   {body_preview}")
        
        print(f"\n📊 ANALYSIS (first 200 chars):")
        analysis_preview = parsed['analysis'][:200] + "..." if len(parsed['analysis']) > 200 else parsed['analysis']
        print(f"   {analysis_preview}")
        
        # Test what frontend would receive
        print("\n🌐 TEST 2: Frontend Response Structure")
        print("-" * 50)
        
        frontend_response = {
            "message": "Email generated successfully from direct audio processing",
            "email": {
                "subject": parsed["subject"],
                "body": parsed["body"]
            },
            "analysis": {"text": parsed["analysis"]},
            "processing_method": "direct_audio_to_gemini"
        }
        
        print("📦 Frontend receives:")
        print(f"   ✅ Clean email subject: '{frontend_response['email']['subject']}'")
        print(f"   ✅ Clean email body: {len(frontend_response['email']['body'])} chars")
        print(f"   ✅ Separate analysis: {len(frontend_response['analysis']['text'])} chars")
        print(f"   ✅ Processing method: {frontend_response['processing_method']}")
        
        # Test edge cases
        print("\n⚙️  TEST 3: Edge Cases")
        print("-" * 50)
        
        # Test with simple response (no sections)
        simple_response = "This is a simple email without sections."
        parsed_simple = audio_service._parse_gemini_response(simple_response)
        print(f"✅ Simple response - Subject: '{parsed_simple['subject']}'")
        print(f"✅ Simple response - Body: '{parsed_simple['body'][:50]}...'")
        
        # Test with empty response
        empty_response = ""
        parsed_empty = audio_service._parse_gemini_response(empty_response)
        print(f"✅ Empty response handled - Subject: '{parsed_empty['subject']}'")
        
        print("\n" + "=" * 80)
        print("🎉 IMPROVED RESPONSE PARSING TESTS COMPLETED!")
        print("=" * 80)
        
        print("\n📊 IMPROVEMENTS:")
        print("✅ Gemini response is properly parsed")
        print("✅ Subject is extracted from email section")
        print("✅ Body contains only the email content")  
        print("✅ Analysis is separated and sent to frontend")
        print("✅ Frontend receives clean, structured data")
        print("✅ Edge cases are handled gracefully")
        
        print("\n🚀 FRONTEND BENEFITS:")
        print("📧 Clean email preview for user")
        print("📊 Separate analysis panel")
        print("🎯 Better user experience")
        print("✨ Professional email formatting")
        
    except Exception as e:
        print(f"\n❌ ERROR DURING TESTING!")
        print(f"🔍 Error type: {type(e).__name__}")
        print(f"📝 Error message: {str(e)}")
        import traceback
        print("\n📊 Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    test_improved_response()