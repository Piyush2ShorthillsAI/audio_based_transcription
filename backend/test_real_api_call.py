#!/usr/bin/env python3
"""Test the actual API call that frontend is making"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_real_api_call():
    """Test the exact same API call that frontend is making"""
    print("🔍 TESTING REAL API CALL FROM FRONTEND")
    print("=" * 80)
    
    try:
        # Step 1: Login to get token (like frontend does)
        print("🔐 Step 1: Login")
        print("-" * 40)
        
        login_data = {
            "username": "test@example.com",
            "password": "test123"
        }
        
        login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            token = login_result.get("access_token")
            print(f"✅ Got token: {token[:20]}...")
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        else:
            print(f"❌ Login failed: {login_response.text}")
            print("Let me try without auth...")
            headers = {"Content-Type": "application/json"}
        
        # Step 2: Get some real recording IDs
        print(f"\n📋 Step 2: Get Real Recording IDs")
        print("-" * 40)
        
        # Get user info first
        if 'Authorization' in headers:
            me_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
            if me_response.status_code == 200:
                user_data = me_response.json()
                print(f"✅ User ID: {user_data.get('id')}")
            else:
                print(f"⚠️  Could not get user info: {me_response.status_code}")
        
        # Step 3: Make the exact API call that frontend makes
        print(f"\n🎯 Step 3: Make Exact Frontend API Call")
        print("-" * 40)
        
        # Using recording IDs from our previous test
        api_request = {
            "action_recording_id": "5ad4b2dc-eafd-4947-8a66-07bfb8c9a0be",  # From our test
            "context_recording_id": "f88f3653-3f6a-4a48-8183-49cc246f38cb",  # From our test
            "contact_id": "790ecab1-c909-493d-94e5-03ff8d216f4a",  # Some contact ID
            "recipient_name": "Test Contact",
            "recipient_email": "test@contact.com"
        }
        
        print(f"📤 Request data:")
        print(json.dumps(api_request, indent=2))
        
        print(f"\n📡 Making POST request to /audio/generate-dual-email...")
        
        response = requests.post(
            f"{BASE_URL}/audio/generate-dual-email",
            json=api_request,
            headers=headers,
            timeout=60  # Give it time to process
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ SUCCESS! API call worked")
            result = response.json()
            print(f"📧 Email length: {len(str(result.get('email', '')))}")
            print(f"🔧 Processing method: {result.get('processing_method')}")
            print(f"📊 Analysis: {result.get('analysis', {})}")
            
            print(f"\n📧 Generated Email:")
            print("-" * 50)
            email_content = result.get('email', '')
            if len(email_content) > 200:
                print(f"{email_content[:200]}...")
            else:
                print(email_content)
            print("-" * 50)
            
        else:
            print("❌ API CALL FAILED!")
            print(f"📝 Response Text: {response.text}")
            
            # Try to parse error details
            try:
                error_data = response.json()
                print(f"📋 Error Detail: {error_data.get('detail', 'No detail')}")
            except:
                print("📋 Could not parse error as JSON")
        
        print(f"\n" + "=" * 80)
        print("🎯 TEST COMPLETED")
        print("=" * 80)
        
        if response.status_code != 200:
            print("💡 TROUBLESHOOTING:")
            print("1. Check if the recording IDs exist in database")
            print("2. Check if audio files exist on disk")
            print("3. Check server logs for detailed error")
            print("4. Verify Gemini API key is working")
        
    except Exception as e:
        print(f"\n❌ ERROR DURING TEST!")
        print(f"🔍 Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_real_api_call()