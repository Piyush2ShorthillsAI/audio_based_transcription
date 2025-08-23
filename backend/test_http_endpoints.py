#!/usr/bin/env python3
"""Test HTTP endpoints after database fix"""

import requests
import time

BASE_URL = "http://localhost:8000"

def test_endpoints():
    print("🌐 TESTING HTTP ENDPOINTS AFTER DATABASE FIX")
    print("=" * 50)
    
    # Test 1: Server health
    print("1️⃣ Testing server health...")
    try:
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Server is healthy")
        else:
            print(f"❌ Health check failed: {health_response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return
    
    # Test 2: Get working credentials 
    print("\n2️⃣ Testing authentication...")
    login_data = {"login": "debug@test.com", "password": "debug123"}
    
    try:
        login_response = requests.post(
            f"{BASE_URL}/auth/login", 
            json=login_data, 
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            print(f"✅ Authentication successful! Token: {token[:20]}...")
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return
            
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return
    
    # Test 3: Check if audio upload works (without file - should give 422)
    print("\n3️⃣ Testing audio upload endpoint access...")
    try:
        upload_response = requests.post(
            f"{BASE_URL}/audio/upload",
            headers=headers,
            data={"title": "test", "audio_type": "action"},
            timeout=10
        )
        
        print(f"Upload endpoint status: {upload_response.status_code}")
        
        if upload_response.status_code == 422:
            print("✅ Audio upload endpoint is accessible (422 = missing file, expected)")
        elif upload_response.status_code == 401:
            print("❌ Still getting 401 - authentication issue")
        elif upload_response.status_code == 500:
            print("❌ Getting 500 - server error (our target to fix)")
            print(f"Response: {upload_response.text}")
        else:
            print(f"ℹ️ Unexpected status: {upload_response.status_code}")
            print(f"Response: {upload_response.text}")
            
    except Exception as e:
        print(f"❌ Upload test failed: {e}")
    
    # Test 4: Check available audio recordings
    print("\n4️⃣ Checking available audio recordings...")
    try:
        # Try to get user recordings (this would test database connection)
        recordings_response = requests.get(
            f"{BASE_URL}/audio/recordings",
            headers=headers,
            timeout=10
        )
        
        print(f"Recordings endpoint status: {recordings_response.status_code}")
        
        if recordings_response.status_code == 200:
            recordings = recordings_response.json()
            print(f"✅ Found {len(recordings)} recordings")
            
            if len(recordings) >= 2:
                print("✅ Sufficient recordings for dual email generation test")
                # Could test email generation here with real recording IDs
            else:
                print("ℹ️ Need to upload audio from frontend first")
                
        elif recordings_response.status_code == 500:
            print("❌ 500 error on recordings - database connection still broken")
            print(f"Response: {recordings_response.text}")
        else:
            print(f"⚠️ Recordings check returned: {recordings_response.status_code}")
            
    except Exception as e:
        print(f"❌ Recordings check failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 SUMMARY:")
    print("If audio upload endpoint returns 422 (not 500), the fix worked!")
    print("If you still get 500 errors, check server logs.")
    print("\n🚀 NOW TRY THE FRONTEND:")
    print("1. Go to http://localhost:5173")
    print("2. Login with: debug@test.com / debug123")
    print("3. Record and generate email")
    print("4. Should work now! 🎉")

if __name__ == "__main__":
    test_endpoints()