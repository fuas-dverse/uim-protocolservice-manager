#!/usr/bin/env python3
"""
Test script for Discovery Service

Tests the LLM-based service discovery endpoint.
Run this after starting the API to verify discovery works.
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_discovery(query: str):
    """Test a discovery query"""
    print(f"\n{'='*70}")
    print(f"Testing Query: {query}")
    print(f"{'='*70}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/discovery/discover",
            json={"user_query": query},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS")
            print(f"\nSelected Service: {result['selected_name']}")
            print(f"Reasoning: {result['reasoning']}")
            print(f"\nService Details:")
            service = result['service']
            print(f"  - Description: {service.get('description', 'N/A')[:100]}...")
            print(f"  - URL: {service.get('service_url', 'N/A')}")
            print(f"  - Number of Intents: {len(service.get('intents', []))}")
            
            # Show intent tags
            all_tags = set()
            for intent in service.get('intents', []):
                all_tags.update(intent.get('tags', []))
            print(f"  - Available Tags: {', '.join(sorted(all_tags))}")
            
            return True
        else:
            print(f"❌ FAILED")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error - Is the API running on {BASE_URL}?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_health():
    """Test discovery health endpoint"""
    print(f"\n{'='*70}")
    print(f"Testing Discovery Health Check")
    print(f"{'='*70}")
    
    try:
        response = requests.get(f"{BASE_URL}/discovery/health")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Discovery service is healthy")
            print(f"Details: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print(f"❌ Health check failed")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "="*70)
    print("  DISCOVERY SERVICE TEST SUITE")
    print("="*70)
    
    # Test health first
    health_ok = test_health()
    
    if not health_ok:
        print("\n⚠️  Health check failed - discovery service may not be available")
        print("   Make sure:")
        print("   1. API is running (python StartupService.py)")
        print("   2. Ollama is running (ollama serve)")
        print("   3. llama3.2 model is available (ollama pull llama3.2)")
        exit(1)
    
    # Test queries
    test_queries = [
        "Find papers about needle in a haystack context problem with LLMs",
        "What's the weather in Amsterdam?",
        "Show me trending repositories on GitHub",
        "Search for songs by The Beatles",
        "Get the latest technology news"
    ]
    
    results = []
    for query in test_queries:
        result = test_discovery(query)
        results.append(result)
    
    # Summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)
    passed = sum(results)
    total = len(results)
    print(f"\nTests Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed!")
        exit(0)
    else:
        print("⚠️  Some tests failed")
        exit(1)
