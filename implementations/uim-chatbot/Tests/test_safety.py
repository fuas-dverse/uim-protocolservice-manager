#!/usr/bin/env python3
"""
Safety Test Suite for DVerse

Tests that the system properly handles malformed requests, enforces input validation,
and provides clear error messages without exposing sensitive information.

Test Categories (from Research doc):
- Invalid input handling
- Malformed request rejection
- Safe error messages (no data leaks)

Test Cases:
1. Invalid JSON format to /query
2. Missing required fields
3. Empty query string
"""
import asyncio
import sys
import os
import httpx

# Configuration
API_BASE_URL = "http://localhost:8000"
CHATBOT_BASE_URL = "http://localhost:8001"


async def test_invalid_json_format():
    """
    TEST 1: Invalid JSON Format
    
    Send malformed JSON to the query endpoint.
    Expected: HTTP 422 with validation error, no server crash.
    """
    print("\n" + "=" * 70)
    print("SAFETY TEST 1: Invalid JSON Format")
    print("=" * 70)
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Send invalid JSON (missing closing brace)
            response = await client.post(
                f"{API_BASE_URL}/query/",
                content='{"query": "test", "agent_id": "test"',  # Invalid JSON
                headers={"Content-Type": "application/json"}
            )
            
            # Should return 422 Unprocessable Entity
            assert response.status_code == 422, f"Expected 422, got {response.status_code}"
            
            # Should have error detail
            data = response.json()
            assert "detail" in data, "Response should contain 'detail' field"
            
            # Should NOT expose internal paths or stack traces
            response_text = str(data).lower()
            sensitive_patterns = ["/home/", "/usr/", "traceback", "file \"", "line "]
            for pattern in sensitive_patterns:
                assert pattern not in response_text, f"Response should not expose: {pattern}"
            
            print("✅ SAFETY TEST 1 PASSED")
            print(f"   ✓ Returned HTTP 422 as expected")
            print(f"   ✓ Error message is safe (no sensitive info)")
            print(f"   ✓ Server did not crash")
            
            return True
            
    except AssertionError as e:
        print(f"❌ SAFETY TEST 1 FAILED: {e}")
        return False
    except httpx.ConnectError:
        print("❌ SAFETY TEST 1 FAILED: Cannot connect to API")
        print("   Make sure API is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ SAFETY TEST 1 FAILED WITH EXCEPTION: {e}")
        return False


async def test_missing_required_fields():
    """
    TEST 2: Missing Required Fields
    
    Send request with missing required parameters.
    Expected: HTTP 422 with clear error indicating which field is missing.
    """
    print("\n" + "=" * 70)
    print("SAFETY TEST 2: Missing Required Fields")
    print("=" * 70)
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Send request missing 'query' field
            response = await client.post(
                f"{API_BASE_URL}/query/",
                json={"agent_id": "test-agent"}  # Missing 'query'
            )
            
            # Should return 422 Unprocessable Entity
            assert response.status_code == 422, f"Expected 422, got {response.status_code}"
            
            data = response.json()
            assert "detail" in data, "Response should contain 'detail' field"
            
            # Error should mention the missing field
            detail_str = str(data["detail"]).lower()
            assert "query" in detail_str or "required" in detail_str or "field" in detail_str, \
                "Error should indicate which field is missing"
            
            print("✅ SAFETY TEST 2 PASSED")
            print(f"   ✓ Returned HTTP 422 for missing field")
            print(f"   ✓ Error message indicates the problem")
            
            return True
            
    except AssertionError as e:
        print(f"❌ SAFETY TEST 2 FAILED: {e}")
        return False
    except httpx.ConnectError:
        print("❌ SAFETY TEST 2 FAILED: Cannot connect to API")
        return False
    except Exception as e:
        print(f"❌ SAFETY TEST 2 FAILED WITH EXCEPTION: {e}")
        return False


async def test_empty_query_string():
    """
    TEST 3: Empty Query String
    
    Send a valid request structure but with empty query.
    Expected: Handled gracefully, either returns empty results or helpful message.
    """
    print("\n" + "=" * 70)
    print("SAFETY TEST 3: Empty Query String")
    print("=" * 70)
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{API_BASE_URL}/query/",
                json={
                    "query": "",
                    "agent_id": "test-agent",
                    "use_ai": False
                }
            )
            
            # Should NOT crash - either 200 with empty results or 400/422 with message
            assert response.status_code in [200, 400, 422], \
                f"Expected 200/400/422, got {response.status_code}"
            
            data = response.json()
            
            # Should return valid JSON response
            assert isinstance(data, dict), "Response should be a JSON object"
            
            # If 200, should have results field (possibly empty)
            # If 400/422, should have detail/error field
            has_valid_structure = (
                "results" in data or 
                "services" in data or 
                "detail" in data or 
                "error" in data or
                "message" in data
            )
            assert has_valid_structure, "Response should have recognizable structure"
            
            print("✅ SAFETY TEST 3 PASSED")
            print(f"   ✓ Returned HTTP {response.status_code}")
            print(f"   ✓ Empty query handled gracefully (no crash)")
            print(f"   ✓ Response has valid structure")
            
            return True
            
    except AssertionError as e:
        print(f"❌ SAFETY TEST 3 FAILED: {e}")
        return False
    except httpx.ConnectError:
        print("❌ SAFETY TEST 3 FAILED: Cannot connect to API")
        return False
    except Exception as e:
        print(f"❌ SAFETY TEST 3 FAILED WITH EXCEPTION: {e}")
        return False


async def run_all_tests():
    """Run all safety tests"""
    print("\n" + "=" * 70)
    print("  DVERSE SAFETY TEST SUITE")
    print("  Testing input validation and error handling")
    print("=" * 70)
    
    # Check API is running
    print("\n🔍 Checking prerequisites...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            health = await client.get(f"{API_BASE_URL}/health")
            if health.status_code != 200:
                print(f"❌ API not healthy: {health.status_code}")
                return 1
            print("✅ API is running")
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("   Make sure API is running: python StartupService.py")
        return 1
    
    results = []
    
    # Run all safety tests
    results.append(await test_invalid_json_format())
    results.append(await test_missing_required_fields())
    results.append(await test_empty_query_string())
    
    # Summary
    print("\n" + "=" * 70)
    print("  SAFETY TEST SUMMARY")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL SAFETY TESTS PASSED!")
        print("\n🛡️  System safety validated:")
        print("   • Invalid JSON handled correctly")
        print("   • Missing fields detected and reported")
        print("   • Empty queries handled gracefully")
        return 0
    else:
        print(f"\n⚠️  {total - passed} safety test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
