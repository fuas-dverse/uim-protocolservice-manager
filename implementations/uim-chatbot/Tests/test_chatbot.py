#!/usr/bin/env python3
"""
Test Suite for DVerse Chatbot HTTP Interface

Tests the chatbot's HTTP /chat endpoint with the current fast_system architecture.

NOTE: This tests the chatbot service (port 8001), not the backend API (port 8000).
The chatbot uses template-based formatting (no LLM), so we test for consistent responses.
"""
import httpx
import asyncio
import json
import sys
import os

# Add parent directory to path for imports
PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PARENT_DIR)


async def test_chatbot_health():
    """Test 1: Chatbot health check endpoint"""
    print("\n" + "=" * 70)
    print("TEST 1: Chatbot Health Check")
    print("=" * 70)

    base_url = "http://localhost:8001"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{base_url}/")

            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            data = response.json()

            # Validate response structure
            assert "service" in data, "Response should have 'service' field"
            assert "status" in data, "Response should have 'status' field"
            assert data["status"] == "running", "Status should be 'running'"

            print(" TEST 1 PASSED")
            print(f"    Chatbot service is running")
            print(f"    Service: {data.get('service')}")
            print(f"    Version: {data.get('version')}")
            print(f"    Architecture: {data.get('architecture')}")

            return True

    except AssertionError as e:
        print(f" TEST 1 FAILED: {e}")
        return False
    except httpx.ConnectError:
        print(" TEST 1 FAILED: Cannot connect to chatbot service")
        print("   Make sure chatbot is running on http://localhost:8001")
        print("   Run: cd implementations/uim-chatbot && python main.py")
        return False
    except Exception as e:
        print(f" TEST 1 FAILED WITH EXCEPTION: {e}")
        return False


async def test_chatbot_query_arxiv():
    """Test 2: Chatbot query with arXiv (success case)"""
    print("\n" + "=" * 70)
    print("TEST 2: Chatbot Query - arXiv Papers")
    print("=" * 70)

    base_url = "http://localhost:8001"

    query = {
        "user_id": "test-user-e2e",
        "message": "Find papers about transformer attention mechanisms",
        "context": {}
    }

    print(f" Query: {query['message']}")
    print(f"️  Timeout: 60 seconds (template formatting is fast)")
    print()

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{base_url}/chat",
                json=query
            )

            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            result = response.json()

            # Validate response structure
            assert "user_id" in result, "Response should have 'user_id'"
            assert "message" in result, "Response should have 'message'"
            assert "query" in result, "Response should have 'query'"
            assert "success" in result, "Response should have 'success'"

            assert result["success"] is True, "Query should succeed"
            assert result["user_id"] == query["user_id"], "User ID should match"
            assert result["query"] == query["message"], "Query should match"

            # Validate message content (template-based formatting)
            message = result["message"].lower()

            # Should contain papers/results
            assert any(word in message for word in ["paper", "found", "result"]), \
                "Response should mention papers or results"

            # Should not be an error
            assert "error" not in message or "no papers found" in message, \
                f"Response should not contain errors: {result['message'][:200]}"

            print(" TEST 2 PASSED")
            print(f"    Query processed successfully")
            print(f"    Template formatting worked")
            print(f"    Response contains paper information")
            print(f"\n Response preview:")
            print(f"   {result['message'][:250]}...")

            return True

    except AssertionError as e:
        print(f" TEST 2 FAILED: {e}")
        return False
    except httpx.TimeoutException:
        print(" TEST 2 FAILED: Request timed out")
        print("   The chatbot should respond within 60 seconds with template formatting")
        print("   Check chatbot logs for errors")
        return False
    except Exception as e:
        print(f" TEST 2 FAILED WITH EXCEPTION: {e}")
        return False


async def test_chatbot_query_with_auth_error():
    """Test 3: Chatbot query with auth error (News API)"""
    print("\n" + "=" * 70)
    print("TEST 3: Chatbot Query - News API (Auth Error Expected)")
    print("=" * 70)

    base_url = "http://localhost:8001"

    query = {
        "user_id": "test-user-auth",
        "message": "Find news about artificial intelligence",
        "context": {}
    }

    print(f" Query: {query['message']}")
    print(f"️  Expected: Authentication error (News API requires key)")
    print()

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{base_url}/chat",
                json=query
            )

            # Either 200 with error message, or 500 error
            assert response.status_code in [200, 500], \
                f"Expected 200 or 500, got {response.status_code}"

            if response.status_code == 200:
                result = response.json()

                # Should have error in message
                message = result["message"].lower()
                error_indicators = ["error", "failed", "authentication", "unauthorized", "api key"]
                has_error = any(indicator in message for indicator in error_indicators)

                assert has_error, f"Response should indicate error but got: {result['message'][:200]}"

                print(" TEST 3 PASSED")
                print(f"    Authentication error handled gracefully")
                print(f"    Chatbot returned error message to user")
                print(f"    Service didn't crash on auth failure")
                print(f"\n️  Error message:")
                print(f"   {result['message'][:200]}")

            else:  # 500 error
                print(" TEST 3 PASSED")
                print(f"    Authentication error caused 500 (acceptable)")
                print(f"    Error was caught and reported")

            return True

    except AssertionError as e:
        print(f" TEST 3 FAILED: {e}")
        return False
    except Exception as e:
        print(f" TEST 3 FAILED WITH EXCEPTION: {e}")
        return False


async def test_chatbot_response_format():
    """Test 4: Validate response format matches ChatbotResponse model"""
    print("\n" + "=" * 70)
    print("TEST 4: Response Format Validation")
    print("=" * 70)

    base_url = "http://localhost:8001"

    query = {
        "user_id": "test-format",
        "message": "Find papers about machine learning",
        "context": {}
    }

    print(f" Testing: Response format matches ChatbotResponse model")
    print()

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{base_url}/chat",
                json=query
            )

            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            result = response.json()

            # Required fields from ChatbotResponse model
            required_fields = ["user_id", "message", "query", "success", "timestamp"]
            for field in required_fields:
                assert field in result, f"Response missing required field: {field}"
                assert result[field] is not None, f"Field '{field}' should not be None"

            # Optional fields
            optional_fields = ["services_discovered", "service_invocation", "error"]
            for field in optional_fields:
                # Just check they exist, can be None/empty
                assert field in result, f"Response missing field: {field}"

            # Validate types
            assert isinstance(result["user_id"], str), "user_id should be string"
            assert isinstance(result["message"], str), "message should be string"
            assert isinstance(result["query"], str), "query should be string"
            assert isinstance(result["success"], bool), "success should be boolean"
            assert isinstance(result["timestamp"], str), "timestamp should be string"

            print(" TEST 4 PASSED")
            print(f"    All required fields present")
            print(f"    Field types are correct")
            print(f"    Response matches ChatbotResponse model")

            return True

    except AssertionError as e:
        print(f" TEST 4 FAILED: {e}")
        return False
    except Exception as e:
        print(f" TEST 4 FAILED WITH EXCEPTION: {e}")
        return False


async def run_all_tests():
    """Run all chatbot HTTP tests"""
    print("\n" + "=" * 70)
    print("  CHATBOT HTTP ENDPOINT TEST SUITE")
    print("  Testing: /chat endpoint with fast_system architecture")
    print("=" * 70)

    results = []

    # Test 1: Health check
    results.append(await test_chatbot_health())

    # Test 2: Successful query (arXiv)
    results.append(await test_chatbot_query_arxiv())

    # Test 3: Auth error handling (News API)
    results.append(await test_chatbot_query_with_auth_error())

    # Test 4: Response format validation
    results.append(await test_chatbot_response_format())

    # Summary
    print("\n" + "=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)
    passed = sum(results)
    total = len(results)

    print(f"\nTests Passed: {passed}/{total}")

    if passed == total:
        print("\n ALL CHATBOT TESTS PASSED!")
        print("\n Chatbot HTTP interface is working:")
        print("   • Health endpoint responds correctly")
        print("   • Processes queries successfully")
        print("   • Handles authentication errors gracefully")
        print("   • Response format matches model specification")
        print("   • Template-based formatting works (no LLM needed)")
        return 0
    else:
        print(f"\n️  {total - passed} test(s) failed")
        print("\nDebugging steps:")
        print("1. Make sure chatbot is running: python main.py")
        print("2. Verify backend API is running on port 8000")
        print("3. Check that MongoDB is seeded with services")
        print("4. Review chatbot logs for detailed errors")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)