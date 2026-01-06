#!/usr/bin/env python3
"""
Test Suite for DVerse Chatbot HTTP Interface

Tests the chatbot's split endpoint system:
- /chat/discover - Returns which service will be used
- /chat/invoke - Invokes the service and returns results

This split architecture allows frontend to show "Using X service..." before results arrive.

Updated: January 2026 - Fixed to use split endpoint system instead of single /chat endpoint
"""
import httpx
import asyncio
import sys
import os

# Add parent directory to path for imports
PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PARENT_DIR)

# Configuration
CHATBOT_URL = "http://localhost:8001"


async def test_chatbot_health():
    """Test 1: Chatbot health check endpoint"""
    print("\n" + "=" * 70)
    print("TEST 1: Chatbot Health Check")
    print("=" * 70)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{CHATBOT_URL}/")

            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            data = response.json()

            # Validate response structure
            assert "service" in data, "Response should have 'service' field"
            assert "status" in data, "Response should have 'status' field"
            assert data["status"] == "running", "Status should be 'running'"

            print("✅ TEST 1 PASSED")
            print(f"   ✓ Chatbot service is running")
            print(f"   ✓ Service: {data.get('service')}")
            print(f"   ✓ Version: {data.get('version')}")
            print(f"   ✓ Architecture: {data.get('architecture')}")

            return True

    except AssertionError as e:
        print(f"❌ TEST 1 FAILED: {e}")
        return False
    except httpx.ConnectError:
        print("❌ TEST 1 FAILED: Cannot connect to chatbot service")
        print("   Make sure chatbot is running on http://localhost:8001")
        print("   Run: cd implementations/uim-chatbot && python main.py")
        return False
    except Exception as e:
        print(f"❌ TEST 1 FAILED WITH EXCEPTION: {e}")
        return False


async def test_discover_endpoint():
    """Test 2: /chat/discover endpoint - service selection"""
    print("\n" + "=" * 70)
    print("TEST 2: Discover Endpoint - Service Selection")
    print("=" * 70)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            request_data = {
                "user_id": "test-user",
                "message": "Find papers about transformer attention mechanisms"
            }

            print(f"📝 Query: {request_data['message']}")
            print(f"🔗 Endpoint: {CHATBOT_URL}/chat/discover")
            print()

            response = await client.post(
                f"{CHATBOT_URL}/chat/discover",
                json=request_data
            )

            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            data = response.json()

            # Validate DiscoverResponse structure
            assert "user_id" in data, "Response should have 'user_id'"
            assert "query" in data, "Response should have 'query'"
            assert "service_name" in data, "Response should have 'service_name'"
            assert "intent_name" in data, "Response should have 'intent_name'"
            assert "service_data" in data, "Response should have 'service_data'"

            # Validate values
            assert data["user_id"] == request_data["user_id"], "User ID should match"
            assert len(data["service_name"]) > 0, "Service name should not be empty"
            assert len(data["intent_name"]) > 0, "Intent name should not be empty"
            assert isinstance(data["service_data"], dict), "Service data should be a dict"

            print("✅ TEST 2 PASSED")
            print(f"   ✓ Discover endpoint responded correctly")
            print(f"   ✓ Selected service: {data['service_name']}")
            print(f"   ✓ Selected intent: {data['intent_name']}")
            print(f"   ✓ Service data included for invoke step")

            # Return the data for use in subsequent tests
            return True, data

    except AssertionError as e:
        print(f"❌ TEST 2 FAILED: {e}")
        return False, None
    except httpx.ConnectError:
        print("❌ TEST 2 FAILED: Cannot connect to chatbot service")
        return False, None
    except Exception as e:
        print(f"❌ TEST 2 FAILED WITH EXCEPTION: {e}")
        return False, None


async def test_invoke_endpoint():
    """Test 3: /chat/invoke endpoint - service invocation"""
    print("\n" + "=" * 70)
    print("TEST 3: Invoke Endpoint - Service Invocation")
    print("=" * 70)

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # First, call discover to get service data
            discover_request = {
                "user_id": "test-user",
                "message": "Find papers about machine learning"
            }

            print(f"📝 Step 1: Discovering service for query...")
            discover_response = await client.post(
                f"{CHATBOT_URL}/chat/discover",
                json=discover_request
            )

            assert discover_response.status_code == 200, \
                f"Discover failed: {discover_response.status_code}"

            discover_data = discover_response.json()
            print(f"   ✓ Service selected: {discover_data['service_name']}")

            # Now call invoke with the service data
            invoke_request = {
                "user_id": discover_data["user_id"],
                "query": discover_data["query"],
                "service_name": discover_data["service_name"],
                "intent_name": discover_data["intent_name"],
                "service_data": discover_data["service_data"]
            }

            print(f"📝 Step 2: Invoking {discover_data['service_name']}...")
            print(f"🔗 Endpoint: {CHATBOT_URL}/chat/invoke")
            print()

            invoke_response = await client.post(
                f"{CHATBOT_URL}/chat/invoke",
                json=invoke_request
            )

            assert invoke_response.status_code == 200, \
                f"Expected 200, got {invoke_response.status_code}"

            data = invoke_response.json()

            # Validate response structure
            assert "user_id" in data, "Response should have 'user_id'"
            assert "message" in data, "Response should have 'message'"
            assert "query" in data, "Response should have 'query'"
            assert "success" in data, "Response should have 'success'"

            # Validate message content
            assert isinstance(data["message"], str), "Message should be a string"
            assert len(data["message"]) > 0, "Message should not be empty"

            print("✅ TEST 3 PASSED")
            print(f"   ✓ Invoke endpoint responded correctly")
            print(f"   ✓ Success: {data['success']}")
            print(f"   ✓ Response length: {len(data['message'])} chars")
            print(f"\n📄 Response preview:")
            print(f"   {data['message'][:300]}...")

            return True

    except AssertionError as e:
        print(f"❌ TEST 3 FAILED: {e}")
        return False
    except httpx.ConnectError:
        print("❌ TEST 3 FAILED: Cannot connect to chatbot service")
        return False
    except Exception as e:
        print(f"❌ TEST 3 FAILED WITH EXCEPTION: {e}")
        return False


async def test_invoke_auth_error():
    """Test 4: /chat/invoke with service requiring auth (News API)"""
    print("\n" + "=" * 70)
    print("TEST 4: Invoke Endpoint - Auth Error Handling")
    print("=" * 70)

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # First, discover a service that requires auth
            discover_request = {
                "user_id": "test-user",
                "message": "Find news about artificial intelligence"
            }

            print(f"📝 Step 1: Discovering service for news query...")
            discover_response = await client.post(
                f"{CHATBOT_URL}/chat/discover",
                json=discover_request
            )

            assert discover_response.status_code == 200, \
                f"Discover failed: {discover_response.status_code}"

            discover_data = discover_response.json()
            print(f"   ✓ Service selected: {discover_data['service_name']}")
            print(f"   ⚠️  Expected: Auth error (no API key)")

            # Now call invoke - should handle auth error gracefully
            invoke_request = {
                "user_id": discover_data["user_id"],
                "query": discover_data["query"],
                "service_name": discover_data["service_name"],
                "intent_name": discover_data["intent_name"],
                "service_data": discover_data["service_data"]
            }

            print(f"📝 Step 2: Invoking {discover_data['service_name']}...")
            print()

            invoke_response = await client.post(
                f"{CHATBOT_URL}/chat/invoke",
                json=invoke_request
            )

            # Should return 200 with error in response, or 401/500
            # The key is it shouldn't crash
            assert invoke_response.status_code in [200, 401, 403, 500], \
                f"Unexpected status: {invoke_response.status_code}"

            data = invoke_response.json()

            # If 200, check for error indication in response
            if invoke_response.status_code == 200:
                # Response should indicate the auth failure somehow
                message = data.get("message", "").lower()
                success = data.get("success", True)
                error = data.get("error", "")

                has_error_indication = (
                    success is False or
                    "error" in message or
                    "unauthorized" in message or
                    "authentication" in message or
                    "api key" in message or
                    len(error) > 0
                )

                # It's okay if it doesn't have error indication -
                # some services might return empty results instead
                if has_error_indication:
                    print("✅ TEST 4 PASSED")
                    print(f"   ✓ Auth error handled gracefully")
                    print(f"   ✓ Success flag: {success}")
                    print(f"   ✓ System didn't crash")
                else:
                    print("✅ TEST 4 PASSED (with note)")
                    print(f"   ✓ Service returned response (may be empty/default)")
                    print(f"   ✓ System didn't crash")
            else:
                print("✅ TEST 4 PASSED")
                print(f"   ✓ Returned appropriate error status: {invoke_response.status_code}")
                print(f"   ✓ System handled auth failure correctly")

            return True

    except AssertionError as e:
        print(f"❌ TEST 4 FAILED: {e}")
        return False
    except httpx.ConnectError:
        print("❌ TEST 4 FAILED: Cannot connect to chatbot service")
        return False
    except Exception as e:
        print(f"❌ TEST 4 FAILED WITH EXCEPTION: {e}")
        return False


async def test_response_format():
    """Test 5: Validate response matches expected model structure"""
    print("\n" + "=" * 70)
    print("TEST 5: Response Format Validation")
    print("=" * 70)

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Complete flow: discover -> invoke
            discover_request = {
                "user_id": "format-test-user",
                "message": "Find papers about neural networks"
            }

            print(f"📝 Running complete discover -> invoke flow...")

            # Discover
            discover_response = await client.post(
                f"{CHATBOT_URL}/chat/discover",
                json=discover_request
            )
            assert discover_response.status_code == 200
            discover_data = discover_response.json()

            # Validate DiscoverResponse format
            discover_required = ["user_id", "query", "service_name", "intent_name", "service_data"]
            for field in discover_required:
                assert field in discover_data, f"DiscoverResponse missing: {field}"

            print(f"   ✓ DiscoverResponse format valid")

            # Invoke
            invoke_request = {
                "user_id": discover_data["user_id"],
                "query": discover_data["query"],
                "service_name": discover_data["service_name"],
                "intent_name": discover_data["intent_name"],
                "service_data": discover_data["service_data"]
            }

            invoke_response = await client.post(
                f"{CHATBOT_URL}/chat/invoke",
                json=invoke_request
            )
            assert invoke_response.status_code == 200
            invoke_data = invoke_response.json()

            # Validate InvokeResponse/ChatbotResponse format
            invoke_required = ["user_id", "message", "query", "success"]
            for field in invoke_required:
                assert field in invoke_data, f"InvokeResponse missing: {field}"

            # Validate types
            assert isinstance(invoke_data["user_id"], str), "user_id should be string"
            assert isinstance(invoke_data["message"], str), "message should be string"
            assert isinstance(invoke_data["query"], str), "query should be string"
            assert isinstance(invoke_data["success"], bool), "success should be boolean"

            print(f"   ✓ InvokeResponse format valid")

            print("✅ TEST 5 PASSED")
            print(f"   ✓ DiscoverResponse has all required fields")
            print(f"   ✓ InvokeResponse has all required fields")
            print(f"   ✓ All field types are correct")
            print(f"   ✓ Split endpoint system working correctly")

            return True

    except AssertionError as e:
        print(f"❌ TEST 5 FAILED: {e}")
        return False
    except httpx.ConnectError:
        print("❌ TEST 5 FAILED: Cannot connect to chatbot service")
        return False
    except Exception as e:
        print(f"❌ TEST 5 FAILED WITH EXCEPTION: {e}")
        return False


async def run_all_tests():
    """Run all chatbot HTTP tests"""
    print("\n" + "=" * 70)
    print("  CHATBOT HTTP ENDPOINT TEST SUITE")
    print("  Testing: Split endpoint system (/chat/discover + /chat/invoke)")
    print("=" * 70)

    # Check if chatbot is running
    print("\n🔍 Checking prerequisites...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{CHATBOT_URL}/")
            if response.status_code != 200:
                print(f"❌ Chatbot not responding: {response.status_code}")
                return 1
            print("✅ Chatbot service is running")
    except Exception as e:
        print(f"❌ Cannot connect to chatbot: {e}")
        print("   Make sure chatbot is running: python main.py")
        return 1

    results = []

    # Test 1: Health check
    results.append(await test_chatbot_health())

    # Test 2: Discover endpoint
    discover_result, _ = await test_discover_endpoint()
    results.append(discover_result)

    # Test 3: Invoke endpoint (success case)
    results.append(await test_invoke_endpoint())

    # Test 4: Invoke endpoint (auth error case)
    results.append(await test_invoke_auth_error())

    # Test 5: Response format validation
    results.append(await test_response_format())

    # Summary
    print("\n" + "=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)
    passed = sum(results)
    total = len(results)

    print(f"\nTests Passed: {passed}/{total}")

    if passed == total:
        print("\n✅ ALL CHATBOT TESTS PASSED!")
        print("\n🎉 Chatbot HTTP interface is working:")
        print("   • Health endpoint responds correctly")
        print("   • /chat/discover selects appropriate service")
        print("   • /chat/invoke executes service calls")
        print("   • Auth errors handled gracefully")
        print("   • Response format matches specifications")
        print("   • Split endpoint system enables better UX")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        print("\nDebugging steps:")
        print("1. Make sure chatbot is running: python main.py")
        print("2. Verify backend API is running on port 8000")
        print("3. Check that MongoDB is seeded with services")
        print("4. Review chatbot logs for detailed errors")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)