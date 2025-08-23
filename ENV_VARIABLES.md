# 🔑 Environment Variables for Direct Audio to Gemini System

## ✅ **REQUIRED Variables**

### **1. GEMINI_API_KEY** (Essential)
```bash
GEMINI_API_KEY=your_gemini_2.5_pro_api_key_here
```
- **Purpose**: Direct audio processing with Gemini 2.5 Pro
- **Where to get**: Google AI Studio (https://makersuite.google.com/)
- **Note**: This is the ONLY required variable for audio processing

## ⚙️ **OPTIONAL Variables (Have Defaults)**

### **2. DATABASE_URL** (Optional)
```bash
DATABASE_URL=postgresql://postgres:password@localhost:5432/crm_auth
```
- **Purpose**: PostgreSQL database connection
- **Default**: `postgresql://postgres:password@localhost:5432/crm_auth`
- **Change if**: Your database setup is different

### **3. Server Configuration** (Optional)
```bash
PORT=8000
HOST=0.0.0.0
```
- **Purpose**: FastAPI server settings
- **Defaults**: PORT=8000, HOST=0.0.0.0
- **Change if**: You need different server settings

## 🚫 **NOT NEEDED for Direct Audio System**

These are **NOT required** since we're doing direct audio processing:
```bash
# ❌ Not needed for direct audio:
OPENAI_API_KEY=...        # No transcription step
GOOGLE_SPEECH_KEY=...     # No speech-to-text step
WHISPER_MODEL=...         # No local whisper
```

## 📝 **How to Set Up**

### **Method 1: Create .env file**
```bash
cd backend
nano .env
```
Add this content:
```bash
GEMINI_API_KEY=your_actual_key_here
DATABASE_URL=postgresql://postgres:password@localhost:5432/crm_auth
```

### **Method 2: Export in terminal**
```bash
export GEMINI_API_KEY=your_actual_key_here
export DATABASE_URL=postgresql://postgres:password@localhost:5432/crm_auth
```

### **Method 3: Add to start script**
```bash
#!/bin/bash
export GEMINI_API_KEY=your_actual_key_here
uvicorn main:app --reload
```

## 🎯 **Quick Start**

**Minimal setup (only what's required):**
```bash
cd backend
export GEMINI_API_KEY=your_key_here
uvicorn main:app --reload
```

That's it! Your direct audio to Gemini system will work with just the Gemini API key.

## 🔍 **How to Get Gemini API Key**

1. Go to: https://makersuite.google.com/
2. Sign in with Google account
3. Create new project or use existing
4. Generate API key
5. Copy the key and use it as GEMINI_API_KEY

## ⚠️ **Important Notes**

- **GEMINI_API_KEY is the only required variable** for audio processing
- **DATABASE_URL only needed** if your database setup is different
- **No OpenAI/Whisper keys needed** - we're doing direct audio processing
- **Keep your API keys secure** - don't commit them to git