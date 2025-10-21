#!/usr/bin/env python3
"""
Test script for CiteRight-Multiverse multi-source ingestion system
"""

import sys
import requests
import time
import json

def test_api_connection():
    """Test if the API is running"""
    print("🔍 Testing API connection...")
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API is running")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API")
        print("   Make sure the API is running: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def test_wikipedia_ingestion():
    """Test Wikipedia ingestion"""
    print("\n📚 Testing Wikipedia ingestion...")
    try:
        payload = {
            "query": "quantum mechanics",
            "sources": ["wikipedia"],
            "max_per_source": 2
        }
        
        response = requests.post("http://localhost:8000/ingest-multiverse", json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Wikipedia ingestion successful: {result['total_chunks']} chunks")
            print(f"   Source stats: {result['source_stats']}")
            return True
        else:
            print(f"❌ Wikipedia ingestion failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing Wikipedia ingestion: {e}")
        return False

def test_stackexchange_ingestion():
    """Test StackExchange ingestion"""
    print("\n💬 Testing StackExchange ingestion...")
    try:
        payload = {
            "query": "quantum mechanics",
            "sources": ["stackexchange"],
            "max_per_source": 2
        }
        
        response = requests.post("http://localhost:8000/ingest-multiverse", json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ StackExchange ingestion successful: {result['total_chunks']} chunks")
            print(f"   Source stats: {result['source_stats']}")
            return True
        else:
            print(f"❌ StackExchange ingestion failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing StackExchange ingestion: {e}")
        return False

def test_arxiv_ingestion():
    """Test arXiv ingestion"""
    print("\n📄 Testing arXiv ingestion...")
    try:
        payload = {
            "query": "quantum mechanics",
            "sources": ["arxiv"],
            "max_per_source": 2
        }
        
        response = requests.post("http://localhost:8000/ingest-multiverse", json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ arXiv ingestion successful: {result['total_chunks']} chunks")
            print(f"   Source stats: {result['source_stats']}")
            return True
        else:
            print(f"❌ arXiv ingestion failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing arXiv ingestion: {e}")
        return False

def test_wikidata_ingestion():
    """Test Wikidata ingestion"""
    print("\n🗃️ Testing Wikidata ingestion...")
    try:
        payload = {
            "query": "quantum mechanics",
            "sources": ["wikidata"],
            "max_per_source": 2
        }
        
        response = requests.post("http://localhost:8000/ingest-multiverse", json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Wikidata ingestion successful: {result['total_chunks']} chunks")
            print(f"   Source stats: {result['source_stats']}")
            return True
        else:
            print(f"❌ Wikidata ingestion failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing Wikidata ingestion: {e}")
        return False

def test_multi_source_ingestion():
    """Test multi-source ingestion"""
    print("\n🌌 Testing multi-source ingestion...")
    try:
        payload = {
            "query": "quantum mechanics",
            "sources": ["wikipedia", "stackexchange", "arxiv", "wikidata"],
            "max_per_source": 1
        }
        
        response = requests.post("http://localhost:8000/ingest-multiverse", json=payload, timeout=60)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Multi-source ingestion successful: {result['total_chunks']} chunks")
            print(f"   Source stats: {result['source_stats']}")
            return True
        else:
            print(f"❌ Multi-source ingestion failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing multi-source ingestion: {e}")
        return False

def test_query_with_multiverse_content():
    """Test querying with multi-source content"""
    print("\n🔍 Testing query with multi-source content...")
    try:
        payload = {
            "query": "What is quantum mechanics and how does it differ from classical mechanics?"
        }
        
        response = requests.post("http://localhost:8000/query", json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print("✅ Query successful!")
            print(f"   Answer length: {len(result['answer'])} characters")
            print(f"   Citations: {len(result['citations'])} sources")
            print(f"   Used re-ask: {result['used_reask']}")
            
            # Show first part of answer
            answer_preview = result['answer'][:200] + "..." if len(result['answer']) > 200 else result['answer']
            print(f"   Answer preview: {answer_preview}")
            
            # Show citation sources
            print("   Citation sources:")
            for i, citation in enumerate(result['citations'][:3]):  # Show first 3
                origin = citation.get('origin', 'Unknown')
                source = citation.get('source', 'Unknown')
                print(f"     {i+1}. {origin} — {source}")
            
            return True
        else:
            print(f"❌ Query failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing query: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 CiteRight-Multiverse Test Suite")
    print("=" * 50)
    
    # Test API connection first
    if not test_api_connection():
        print("\n❌ Cannot proceed without API connection")
        sys.exit(1)
    
    # Run individual source tests
    tests = [
        ("Wikipedia", test_wikipedia_ingestion),
        ("StackExchange", test_stackexchange_ingestion),
        ("arXiv", test_arxiv_ingestion),
        ("Wikidata", test_wikidata_ingestion),
        ("Multi-source", test_multi_source_ingestion),
        ("Query", test_query_with_multiverse_content)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            time.sleep(2)  # Brief pause between tests
        except KeyboardInterrupt:
            print("\n\n⚠️ Tests interrupted by user")
            break
        except Exception as e:
            print(f"❌ Unexpected error in {test_name}: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! CiteRight-Multiverse is working correctly.")
        print("\nYou can now:")
        print("   • Use the Streamlit UI: streamlit run ui/streamlit_app.py")
        print("   • Query the API directly: POST /query")
        print("   • Ingest from multiple sources: POST /ingest-multiverse")
    else:
        print("❌ Some tests failed. Check the error messages above.")
        print("\nCommon issues:")
        print("   • Make sure all required packages are installed: pip install -r requirements.txt")
        print("   • Check internet connection for external APIs")
        print("   • Verify Ollama is running with wizardlm2 model")
        
        if passed < 3:  # If most tests failed
            print("   • Consider running individual source tests to isolate issues")
            sys.exit(1)

if __name__ == "__main__":
    main()
