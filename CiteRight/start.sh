#!/bin/bash

# CiteRight RAG Assistant Startup Script

echo "🚀 Starting CiteRight RAG Assistant..."

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "❌ Ollama is not running. Please start Ollama first:"
    echo "   ollama serve"
    echo "   ollama pull wizardlm2:latest"
    exit 1
fi

# Check if wizardlm2 model is available
if ! ollama list | grep -q "wizardlm2"; then
    echo "📥 Pulling wizardlm2 model..."
    ollama pull wizardlm2:latest
fi

echo "✅ Ollama is running with wizardlm2 model"

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "📦 Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# Start the FastAPI server
echo "🌐 Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
API_PID=$!

# Wait a moment for the API to start
sleep 3

# Start Streamlit UI
echo "🖥️  Starting Streamlit UI..."
streamlit run ui/streamlit_app.py --server.port 8501 --server.address 0.0.0.0 &
UI_PID=$!

echo ""
echo "🎉 CiteRight RAG Assistant is running!"
echo "   📊 API: http://localhost:8000"
echo "   🖥️  UI: http://localhost:8501"
echo "   📚 Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $API_PID $UI_PID 2>/dev/null
    exit 0
}

# Trap Ctrl+C
trap cleanup SIGINT

# Wait for processes
wait

