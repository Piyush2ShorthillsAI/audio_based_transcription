#!/usr/bin/env python3
"""
Comprehensive test to simulate the exact frontend flow and identify errors
"""

import requests
import json
import os
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_auth_flow():
    """Test authentication first"""
    print("🔐 Testing authentication...")
    
    # Try to create a test user
    signup_data = {
        "username": "testuser",
        "email": "test@example.com", 
        "password": "testpass123"
    }
    
    print("📝 Attempting signup...")
    signup_response = requests.post(
        f"{BASE_URL}/auth/signup",
        data=signup_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    print(f"Signup status: {signup_response.status_code}")
    
    # Login to get token
    print("🚪 Attempting login...")
    login_data = {
        "login": "test@example.com",
        "password": "testpass123"
    }
    
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Login status: {login_response.status_code}")
    if login_response.status_code != 200:
        print(f"Login error: {login_response.text}")
        return None
    
    token_data = login_response.json()
    access_token = token_data["access_token"]
    print(f"✅ Got access token: {access_token[:20]}...")
    
    return access_token

def test_audio_upload(token, audio_file_path, audio_type):
    """Test uploading a single audio file"""
    print(f"📤 Uploading {audio_type} audio: {audio_file_path}")
    
    if not os.path.exists(audio_file_path):
        print(f"❌ Audio file not found: {audio_file_path}")
        return None
    
    with open(audio_file_path, 'rb') as f:
        files = {
            'audio': (f'{audio_type}.webm', f, 'audio/webm')
        }
        data = {
            'title': f'{audio_type.title()} Audio Test',
            'contact_id': 'test-contact-123',
            'audio_type': audio_type
        }
        headers = {
            'Authorization': f'Bearer {token}'
        }
        
        response = requests.post(
            f"{BASE_URL}/audio/upload",
            files=files,
            data=data,
            headers=headers
        )
        
        print(f"Upload status: {response.status_code}")
        if response.status_code != 200:
            print(f"Upload error: {response.text}")
            return None
        
        result = response.json()
        recording_id = result.get('recording_id')
        print(f"✅ {audio_type.title()} uploaded: {recording_id}")
        return recording_id

def test_email_generation(token, action_id, context_id):
    """Test the email generation endpoint"""
    print("🤖 Testing email generation...")
    
    if not action_id or not context_id:
        print("❌ Missing recording IDs")
        return False
    
    payload = {
        'action_recording_id': action_id,
        'context_recording_id': context_id,
        'contact_id': 'test-contact-123',
        'recipient_name': 'Test User',
        'recipient_email': 'test@example.com'
    }
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        print("🚀 Sending email generation request...")
        response = requests.post(
            f"{BASE_URL}/audio/generate-dual-email",
            json=payload,
            headers=headers,
            timeout=60  # Give it 60 seconds
        )
        
        print(f"📡 Response status: {response.status_code}")
        print(f"📡 Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Email generation successful!")
            print(f"📝 Subject: {result.get('email', {}).get('subject', 'No subject')}")
            email_body = result.get('email', {}).get('body', '')
            print(f"📄 Body length: {len(email_body)} characters")
            if len(email_body) > 0:
                print(f"📄 Body preview: {email_body[:200]}...")
            return True
        else:
            print(f"❌ Email generation failed: {response.status_code}")
            print(f"Error response: {response.text}")
            
            # Try to parse error details
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                pass
                
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"❌ Request failed with exception: {e}")
        return False

def main():
    """Run the complete test flow"""
    print("🧪 Starting comprehensive audio processing test...")
    print("=" * 60)
    
    # Step 1: Authentication
    token = test_auth_flow()
    if not token:
        print("💥 Authentication failed - cannot continue")
        return False
    
    print("\n" + "=" * 60)
    
    # Step 2: Find audio files
    audio_dir = Path("uploads/audio")
    audio_files = list(audio_dir.glob("*.webm"))
    
    if len(audio_files) < 2:
        print(f"❌ Need at least 2 audio files, found {len(audio_files)}")
        return False
    
    # Use the two most recent files
    action_file = str(audio_files[-1])
    context_file = str(audio_files[-2])
    
    print(f"🎵 Using audio files:")
    print(f"  Action: {action_file}")
    print(f"  Context: {context_file}")
    
    # Step 3: Upload audio files
    action_id = test_audio_upload(token, action_file, "action")
    context_id = test_audio_upload(token, context_file, "context")
    
    print("\n" + "=" * 60)
    
    # Step 4: Generate email
    success = test_email_generation(token, action_id, context_id)
    
    print("\n" + "=" * 60)
    print(f"🎯 Overall test result: {'SUCCESS ✅' if success else 'FAILED ❌'}")
    
    return success

if __name__ == "__main__":
    main()