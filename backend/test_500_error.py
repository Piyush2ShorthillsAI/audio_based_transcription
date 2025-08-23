#!/usr/bin/env python3
"""Test the exact 500 error with proper authentication"""

import json
import requests
import time

def test_500_error():
    """Test to reproduce and identify the 500 error"""
    print("🔍 TESTING 500 ERROR WITH PROPER SETUP")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000"
    
    # Step 1: Test health endpoint
    print("\n🏥 Step 1: Health Check")
    print("-" * 30)
    
    try:
        health_response = requests.get(f"{base_url}/health")
        print(f"✅ Health: {health_response.status_code}")
        if health_response.status_code == 200:
            print(f"Response: {health_response.text}")
    except Exception as e:
        print(f"❌ Health failed: {e}")
        return
    
    # Step 2: Get users
    print("\n👥 Step 2: Get Users")
    print("-" * 30)
    
    try:
        users_response = requests.get(f"{base_url}/users/")
        print(f"Users status: {users_response.status_code}")
        
        if users_response.status_code != 200:
            print(f"❌ Cannot get users: {users_response.text}")
            return
            
        users = users_response.json()
        print(f"Found {len(users)} users")
        
        if not users:
            print("❌ No users found")
            return
            
        user = users[0]
        print(f"Using user: {user.get('username', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Users failed: {e}")
        return
    
    # Step 3: Test without authentication (should get 401/403)
    print("\n🔐 Step 3: Test Without Auth")
    print("-" * 30)
    
    payload = {
        "action_recording_id": "test-123",
        "context_recording_id": "test-456",
        "recipient_name": "Test User",
        "recipient_email": "test@example.com"
    }
    
    try:
        no_auth_response = requests.post(
            f"{base_url}/audio/generate-dual-email",
            json=payload,
            timeout=10
        )
        print(f"No auth status: {no_auth_response.status_code}")
        print(f"No auth response: {no_auth_response.text[:200]}...")
        
        if no_auth_response.status_code == 500:
            print("🚨 GETTING 500 WITHOUT AUTH - THIS IS THE PROBLEM!")
            try:
                error_data = no_auth_response.json()
                error_detail = error_data.get('detail', '')
                print(f"🔥 500 ERROR DETAIL: {error_detail}")
            except:
                print("Could not parse error JSON")
                
    except Exception as e:
        print(f"❌ No auth test failed: {e}")
    
    # Step 4: Try with invalid auth (should get 401/403)
    print("\n🔑 Step 4: Test With Invalid Auth")
    print("-" * 30)
    
    headers = {"Authorization": "Bearer invalid-token-123"}
    
    try:
        invalid_auth_response = requests.post(
            f"{base_url}/audio/generate-dual-email",
            json=payload,
            headers=headers,
            timeout=10
        )
        print(f"Invalid auth status: {invalid_auth_response.status_code}")
        print(f"Invalid auth response: {invalid_auth_response.text[:200]}...")
        
        if invalid_auth_response.status_code == 500:
            print("🚨 GETTING 500 WITH INVALID AUTH - AUTH SYSTEM ISSUE!")
            try:
                error_data = invalid_auth_response.json()
                error_detail = error_data.get('detail', '')
                print(f"🔥 500 ERROR DETAIL: {error_detail}")
            except:
                print("Could not parse error JSON")
                
    except Exception as e:
        print(f"❌ Invalid auth test failed: {e}")
    
    # Step 5: Try to get real auth token
    print("\n🎯 Step 5: Try Real Authentication")
    print("-" * 30)
    
    # Common test passwords
    test_passwords = ["password123", "password", "123456", "test123", "admin"]
    token = None
    
    for password in test_passwords:
        try:
            login_data = {
                "username": user.get('username'),
                "password": password
            }
            
            login_response = requests.post(f"{base_url}/auth/login", json=login_data)
            print(f"Login attempt with '{password}': {login_response.status_code}")
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                token = token_data.get('access_token')
                print(f"✅ Got token: {token[:20]}...")
                break
            elif login_response.status_code == 422:
                print("⚠️  422 - Invalid request format")
                break
            else:
                print(f"❌ Login failed: {login_response.text[:100]}")
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            
    if not token:
        print("⚠️  Could not get auth token, testing with fake recording IDs anyway...")
        
        # Step 6: Get user's actual audio recordings 
        print("\n🎵 Step 6: Get Audio Recordings")
        print("-" * 30)
        
        try:
            # Try without auth first
            audio_response = requests.get(f"{base_url}/audio/user/{user['id']}")
            print(f"Audio (no auth): {audio_response.status_code}")
            
            if audio_response.status_code == 200:
                recordings = audio_response.json()
                print(f"Found {len(recordings)} recordings")
                
                action_audio = None
                context_audio = None
                
                for recording in recordings:
                    if recording.get('audio_type') == 'action' and not action_audio:
                        action_audio = recording
                    elif recording.get('audio_type') == 'context' and not context_audio:
                        context_audio = recording
                
                if action_audio and context_audio:
                    print(f"✅ Found both audio types")
                    
                    # Test with real IDs but no auth
                    real_payload = {
                        "action_recording_id": action_audio["id"],
                        "context_recording_id": context_audio["id"],
                        "recipient_name": "Test User",
                        "recipient_email": "test@example.com"
                    }
                    
                    print("\n🎯 Final Test: Real IDs, No Auth")
                    print("-" * 30)
                    
                    try:
                        final_response = requests.post(
                            f"{base_url}/audio/generate-dual-email",
                            json=real_payload,
                            timeout=30
                        )
                        
                        print(f"Final status: {final_response.status_code}")
                        
                        if final_response.status_code == 500:
                            print("🔥 500 ERROR WITH REAL RECORDING IDS!")
                            try:
                                error_data = final_response.json()
                                error_detail = error_data.get('detail', '')
                                print(f"ERROR DETAIL: {error_detail}")
                                
                                # This should show us exactly what's failing
                                if 'line' in error_detail.lower():
                                    print("👆 ERROR SHOWS EXACT LINE!")
                                    
                            except:
                                print(f"Raw error response: {final_response.text}")
                                
                        elif final_response.status_code in [401, 403]:
                            print("✅ Proper auth error (expected)")
                            
                    except Exception as e:
                        print(f"❌ Final test failed: {e}")
                        
                else:
                    print("❌ Missing audio files")
            else:
                print(f"❌ Could not get audio: {audio_response.text}")
                
        except Exception as e:
            print(f"❌ Audio test failed: {e}")

if __name__ == "__main__":
    test_500_error()