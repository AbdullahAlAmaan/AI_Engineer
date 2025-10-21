#!/bin/bash

# CiteRight-Multiverse Setup Script

echo "🌌 Setting up CiteRight-Multiverse..."

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.9+ is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if Ollama is running
echo "🔍 Checking Ollama connection..."
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "⚠️  Ollama is not running. Please start Ollama first:"
    echo "   ollama serve"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Check if wizardlm2 model is available
echo "🤖 Checking for wizardlm2 model..."
if ! ollama list | grep -q "wizardlm2"; then
    echo "📥 Pulling wizardlm2 model (this may take a while)..."
    ollama pull wizardlm2:latest
fi

echo "✅ Ollama setup complete"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/index/faiss
mkdir -p .cursor

# Test the setup
echo "🧪 Running setup tests..."
python test_setup.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 CiteRight-Multiverse setup complete!"
    echo ""
    echo "To start the system:"
    echo "  1. Start the API: uvicorn app.main:app --reload"
    echo "  2. Start the UI: streamlit run ui/streamlit_app.py"
    echo "  3. Or use Docker: docker compose up --build"
    echo ""
    echo "To test multi-source ingestion:"
    echo "  python test_multiverse.py"
    echo ""
    echo "API will be available at: http://localhost:8000"
    echo "UI will be available at: http://localhost:8501"
else
    echo "❌ Setup tests failed. Please check the error messages above."
    exit 1
fi
