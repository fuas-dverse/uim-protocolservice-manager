#!/usr/bin/env python3
"""
Test script to verify the API + AQS merge works correctly.

Run this after starting the unified service to verify all endpoints work.
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_endpoint(name, method, url, data=None, expected_status=200):
    """Test a single endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"{'='*60}")
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == expected_status:
            print(f"✅ {name} - PASSED")
            print(f"Response preview:")
            try:
                print(json.dumps(response.json(), indent=2)[:500])
            except:
                print(response.text[:500])
            return True
        else:
            print(f"❌ {name} - FAILED")
            print(f"Expected: {expected_status}, Got: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ {name} - FAILED (Connection Error)")
        print(f"   Is the service running on {BASE_URL}?")
        return False
    except Exception as e:
        print(f"❌ {name} - FAILED ({str(e)})")
        return False


def main():
    """Run all tests"""
    print("="*60)
    print("UIM Service Manager - Post-Merge Test Suite")
    print("="*60)
    print(f"Testing against: {BASE_URL}")
    print("="*60)
    
    results = []
    
    # Test 1: Root endpoint
    results.append(test_endpoint(
        "Root Endpoint",
        "GET",
        f"{BASE_URL}/"
    ))
    
    # Test 2: Health check
    results.append(test_endpoint(
        "Health Check",
        "GET",
        f"{BASE_URL}/health"
    ))
    
    # Test 3: Services endpoint
    results.append(test_endpoint(
        "Get All Services",
        "GET",
        f"{BASE_URL}/services"
    ))
    
    # Test 4: Intents endpoint
    results.append(test_endpoint(
        "Get All Intents",
        "GET",
        f"{BASE_URL}/intents"
    ))
    
    # Test 5: Query endpoint (keyword mode)
    results.append(test_endpoint(
        "Query Endpoint (Keyword Mode)",
        "POST",
        f"{BASE_URL}/query/",
        data={
            "query": "Find me weather services",
            "agent_id": "test-script",
            "use_ai": False
        }
    ))
    
    # Test 6: Query health check
    results.append(test_endpoint(
        "Query Health Check",
        "GET",
        f"{BASE_URL}/query/health"
    ))
    
    # Test 7: API Documentation
    results.append(test_endpoint(
        "API Documentation",
        "GET",
        f"{BASE_URL}/docs",
        expected_status=200
    ))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! The merge was successful!")
        print("\nNext steps:")
        print("1. Try querying via the browser: http://localhost:8000/docs")
        print("2. Test with your frontend application")
        print("3. (Optional) Test AI mode if you have OPENAI_API_KEY set")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")
        print("\nTroubleshooting:")
        print("1. Make sure the service is running: python StartupService.py")
        print("2. Check the console logs for errors")
        print("3. Verify MongoDB and NATS are running")
        print("4. Review the MERGE_GUIDE.md for setup instructions")
        sys.exit(1)


if __name__ == "__main__":
    main()
