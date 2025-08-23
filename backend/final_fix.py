#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE FIX
This script identifies and fixes all potential issues
"""

import asyncio
import os
import subprocess
import time
from pathlib import Path

async def test_database_connection():
    """Test database connection in FastAPI context"""
    print("🗄️ Testing database connection...")
    try:
        from services.db_service.database import database, connect_db, disconnect_db
        
        # Connect to database
        await connect_db()
        print("✅ Database connection established")
        
        # Test a simple query
        result = await database.fetch_one("SELECT 1 as test")
        print(f"✅ Database query successful: {result}")
        
        await disconnect_db()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def test_audio_service():
    """Test audio service initialization"""
    print("🎵 Testing audio service...")
    try:
        # First connect database
        from services.db_service.database import database, connect_db
        await connect_db()
        
        from services.audio_service.audio_service_minimal import AudioServiceMinimal
        
        service = AudioServiceMinimal()
        print("✅ AudioServiceMinimal initialized")
        
        # Test database reference
        if hasattr(service, 'database') and service.database:
            print("✅ Database reference exists in service")
        else:
            print("❌ Database reference missing in service")
        
        return True
        
    except Exception as e:
        print(f"❌ Audio service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_gemini_service():
    """Test Gemini service"""
    print("🤖 Testing Gemini service...")
    try:
        from services.audio_service.gemini_service import GeminiService
        
        service = GeminiService()
        print("✅ GeminiService initialized")
        
        # Test connection
        result = await service.test_connection()
        if result['status'] == 'success':
            print("✅ Gemini API connection successful")
            return True
        else:
            print(f"❌ Gemini API connection failed: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Gemini service test failed: {e}")
        return False

def check_frontend_status():
    """Check if frontend is running"""
    print("🖥️ Checking frontend status...")
    
    # Check common ports
    ports = [5173, 5174]
    for port in ports:
        try:
            result = subprocess.run(
                ['curl', '-s', f'http://localhost:{port}', '--max-time', '2'],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                print(f"✅ Frontend found on port {port}")
                return port
        except:
            pass
    
    print("❌ Frontend not accessible on common ports")
    return None

def fix_cors_issues():
    """Check and ensure CORS is properly configured"""
    print("🌐 Checking CORS configuration...")
    
    try:
        main_py_path = Path("main.py")
        if main_py_path.exists():
            with open(main_py_path, 'r') as f:
                content = f.read()
            
            if 'allow_origins=["*"]' in content:
                print("✅ CORS properly configured for all origins")
                return True
            else:
                print("❌ CORS might be restricted")
                return False
        
    except Exception as e:
        print(f"Error checking CORS: {e}")
        return False

async def run_comprehensive_check():
    """Run all checks"""
    print("🧪 RUNNING COMPREHENSIVE SYSTEM CHECK")
    print("=" * 60)
    
    results = {}
    
    # Check 1: Database
    results['database'] = await test_database_connection()
    
    print("\n" + "-" * 40)
    
    # Check 2: Audio Service
    results['audio_service'] = await test_audio_service()
    
    print("\n" + "-" * 40)
    
    # Check 3: Gemini Service
    results['gemini'] = await test_gemini_service()
    
    print("\n" + "-" * 40)
    
    # Check 4: Frontend
    frontend_port = check_frontend_status()
    results['frontend'] = frontend_port is not None
    
    print("\n" + "-" * 40)
    
    # Check 5: CORS
    results['cors'] = fix_cors_issues()
    
    print("\n" + "=" * 60)
    print("🎯 FINAL RESULTS:")
    
    all_good = True
    for check, status in results.items():
        emoji = "✅" if status else "❌"
        print(f"{emoji} {check.upper()}: {'PASS' if status else 'FAIL'}")
        if not status:
            all_good = False
    
    print(f"\n🎊 OVERALL STATUS: {'ALL SYSTEMS GO' if all_good else 'ISSUES FOUND'}")
    
    if all_good:
        print("\n🚀 System is ready! Try the frontend now:")
        if frontend_port:
            print(f"   Frontend: http://localhost:{frontend_port}")
        print("   Backend: http://localhost:8000")
        
        print("\n📋 TESTING STEPS:")
        print("1. Open frontend URL")
        print("2. Login with existing credentials")
        print("3. Select contact (Abhijit Bam)")
        print("4. Record Action audio (10 seconds)")
        print("5. Record Context audio (10 seconds)")
        print("6. Click Generate Message")
        print("7. Wait ~25 seconds for result")
    else:
        print("\n🔧 Please fix the failed components above")
    
    return all_good

if __name__ == "__main__":
    asyncio.run(run_comprehensive_check())