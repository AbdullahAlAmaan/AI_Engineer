#!/usr/bin/env python3
"""
Test script to verify CiteRight RAG Assistant setup
"""

import sys
import subprocess
import requests
import time

def test_imports():
    """Test if all required packages can be imported"""
    print("🔍 Testing imports...")
    try:
        import fastapi
        import uvicorn
        import pydantic
        import sentence_transformers
        import langchain
        import faiss
        import rank_bm25
        import numpy
        import streamlit
        import ollama
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_ollama_connection():
    """Test if Ollama is running and accessible"""
    print("🔍 Testing Ollama connection...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            wizardlm2_available = any("wizardlm2" in model.get("name", "") for model in models)
            if wizardlm2_available:
                print("✅ Ollama is running with wizardlm2 model")
                return True
            else:
                print("⚠️  Ollama is running but wizardlm2 model not found")
                print("   Run: ollama pull wizardlm2:latest")
                return False
        else:
            print(f"❌ Ollama API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama")
        print("   Make sure Ollama is running: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Error testing Ollama: {e}")
        return False

def test_app_imports():
    """Test if the app modules can be imported"""
    print("🔍 Testing app imports...")
    try:
        from app.config import settings
        from app.models import QueryRequest, QueryResponse
        from app.rag.utils import chunk_text, build_context
        print("✅ App modules import successfully")
        return True
    except ImportError as e:
        print(f"❌ App import error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 CiteRight RAG Assistant Setup Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_ollama_connection,
        test_app_imports
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! CiteRight is ready to use.")
        print("\nTo start the application:")
        print("   ./start.sh")
        print("   or")
        print("   uvicorn app.main:app --reload")
        print("   streamlit run ui/streamlit_app.py")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
