#!/bin/bash

echo "🚀 Starting CRM Application with Cross-Device Sync"
echo "================================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
if ! command_exists python3; then
    echo "❌ Python3 not found. Please install Python3."
    exit 1
fi

if ! command_exists npm; then
    echo "❌ Node.js/npm not found. Please install Node.js."
    exit 1
fi

# Start backend
echo "🔧 Starting Backend Server..."
cd backend
nohup uvicorn main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!

sleep 3

# Test backend health
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend running on http://localhost:8000"
else
    echo "❌ Backend failed to start"
    exit 1
fi

# Start frontend
echo "🎨 Starting Frontend Server..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "🎉 Application Started Successfully!"
echo "=================================="
echo "📱 Frontend: http://localhost:5174"
echo "🔗 Backend:  http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo ""
echo "🌐 Cross-Device Sync Features:"
echo "  • Login from any device to see your data"
echo "  • Favorites and recents sync across devices"
echo "  • Works offline with localStorage backup"
echo ""
echo "🛑 To stop: Press Ctrl+C or run:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "📊 Logs:"
echo "   Backend: tail -f backend/backend.log"
echo "   Frontend: Check terminal output above"

# Wait for user to stop
wait