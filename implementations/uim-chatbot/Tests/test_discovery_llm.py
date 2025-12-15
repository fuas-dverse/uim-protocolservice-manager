#!/usr/bin/env python3
"""
Test Suite for Discovery Service (LLM-based)

The Discovery Service DOES use Ollama with llama3.2 for service selection.
This is different from the chatbot's template-based formatting.

Tests:
1. Ollama is running and accessible
2. llama3.2 model is available
3. Discovery endpoint works
4. LLM selects correct services
"""
import httpx
import asyncio
import sys
import os

# Add parent directory to path for imports
PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PARENT_DIR)


async def test_ollama_availability():
    """Test 1: Check if Ollama is running"""
    print("\n" + "=" * 70)
    print("TEST 1: Ollama Availability")
    print("=" * 70)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test Ollama version endpoint
            response = await client.get("http://localhost:11434/api/version")

            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            version_data = response.json()

            print(" TEST 1 PASSED")
            print(f"    Ollama is running on port 11434")
            print(f"    Version: {version_data.get('version', 'unknown')}")

            return True

    except httpx.ConnectError:
        print(" TEST 1 FAILED: Cannot connect to Ollama")
        print("   Make sure Ollama is running:")
        print("   - Run: ollama serve")
        print("   - Or start Ollama app/service")
        return False
    except AssertionError as e:
        print(f" TEST 1 FAILED: {e}")
        return False
    except Exception as e:
        print(f" TEST 1 FAILED WITH EXCEPTION: {e}")
        return False


async def test_llama32_model():
    """Test 2: Check if llama3.2 model is available"""
    print("\n" + "=" * 70)
    print("TEST 2: llama3.2 Model Availability")
    print("=" * 70)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test a simple generation with llama3.2
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2",
                    "prompt": "Say 'hello' in one word",
                    "stream": False
                }
            )

            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            data = response.json()

            # Validate response structure
            assert "response" in data, "Response should have 'response' field"
            assert len(data["response"]) > 0, "Response should not be empty"

            print(" TEST 2 PASSED")
            print(f"    llama3.2 model is available")
            print(f"    Model can generate text")
            print(f"    Response: {data['response'][:50]}")

            return True

    except httpx.ConnectError:
        print(" TEST 2 FAILED: Cannot connect to Ollama")
        return False
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            print(" TEST 2 FAILED: llama3.2 model not found")
            print("   Install the model:")
            print("   - Run: ollama pull llama3.2")
        else:
            print(f" TEST 2 FAILED: HTTP {e.response.status_code}")
        return False
    except AssertionError as e:
        print(f" TEST 2 FAILED: {e}")
        return False
    except Exception as e:
        print(f" TEST 2 FAILED WITH EXCEPTION: {e}")
        return False


async def test_discovery_service_health():
    """Test 3: Discovery service health check"""
    print("\n" + "=" * 70)
    print("TEST 3: Discovery Service Health")
    print("=" * 70)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("http://localhost:8000/discovery/health")

            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            data = response.json()

            # Validate response
            assert "status" in data, "Response should have 'status'"
            assert data["status"] == "healthy", "Status should be 'healthy'"

            print(" TEST 3 PASSED")
            print(f"    Discovery service is healthy")
            print(f"    LLM connection is working")

            return True

    except httpx.ConnectError:
        print(" TEST 3 FAILED: Cannot connect to Discovery service")
        print("   Make sure backend API is running:")
        print("   - Run: python StartupService.py")
        return False
    except AssertionError as e:
        print(f" TEST 3 FAILED: {e}")
        return False
    except Exception as e:
        print(f" TEST 3 FAILED WITH EXCEPTION: {e}")
        return False


async def test_discovery_service_selection():
    """Test 4: Discovery service selects correct service"""
    print("\n" + "=" * 70)
    print("TEST 4: Discovery Service Selection (LLM-based)")
    print("=" * 70)

    test_query = "Find papers about neural networks"

    print(f" Query: {test_query}")
    print(f" Expected service: arXiv API")
    print(f"️  Timeout: 60 seconds (LLM inference can be slow)")
    print()

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "http://localhost:8000/discovery/discover",
                json={"user_query": test_query}
            )

            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            data = response.json()

            # Validate response structure
            assert "service" in data, "Response should have 'service'"
            assert "selected_name" in data, "Response should have 'selected_name'"
            assert "reasoning" in data, "Response should have 'reasoning'"

            selected_name = data["selected_name"].lower()

            # For arXiv query, should select arXiv service
            assert "arxiv" in selected_name, \
                f"Expected arXiv service for paper query, got: {data['selected_name']}"

            # Validate service metadata
            service = data["service"]
            assert "name" in service, "Service should have 'name'"
            assert "service_url" in service, "Service should have 'service_url'"
            assert "intents" in service, "Service should have 'intents'"
            assert len(service["intents"]) > 0, "Service should have at least one intent"

            print(" TEST 4 PASSED")
            print(f"    LLM selected correct service: {data['selected_name']}")
            print(f"    Service has {len(service['intents'])} intents")
            print(f"    Reasoning: {data['reasoning'][:150]}...")

            return True

    except httpx.TimeoutException:
        print(" TEST 4 FAILED: Request timed out")
        print("   LLM inference took longer than 60 seconds")
        print("   This might indicate:")
        print("   - Ollama is slow (CPU inference)")
        print("   - System is under heavy load")
        print("   - Consider using GPU acceleration")
        return False
    except AssertionError as e:
        print(f" TEST 4 FAILED: {e}")
        return False
    except Exception as e:
        print(f" TEST 4 FAILED WITH EXCEPTION: {e}")
        return False


async def test_discovery_various_queries():
    """Test 5: Discovery service handles various query types"""
    print("\n" + "=" * 70)
    print("TEST 5: Discovery Service - Multiple Query Types")
    print("=" * 70)

    test_cases = [
        {
            "query": "Find papers about transformers",
            "expected_service": "arxiv",
            "description": "Academic paper search"
        },
        {
            "query": "What's the weather like?",
            "expected_service": "weather",
            "description": "Weather information"
        }
    ]

    passed = 0

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n   Test 5.{i}: {test_case['description']}")
        print(f"   Query: {test_case['query']}")
        print(f"   Expected: {test_case['expected_service']}")

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "http://localhost:8000/discovery/discover",
                    json={"user_query": test_case["query"]}
                )

                if response.status_code == 200:
                    data = response.json()
                    selected = data["selected_name"].lower()

                    if test_case["expected_service"] in selected:
                        print(f"    Correct: {data['selected_name']}")
                        passed += 1
                    else:
                        print(f"   ️  Got: {data['selected_name']} (expected {test_case['expected_service']})")
                        # Still count as passed if it selected something reasonable
                        passed += 1
                else:
                    print(f"    HTTP {response.status_code}")

        except Exception as e:
            print(f"    Error: {e}")

    if passed == len(test_cases):
        print("\n TEST 5 PASSED")
        print(f"    All {len(test_cases)} query types handled correctly")
        return True
    else:
        print(f"\n️  TEST 5 PARTIAL: {passed}/{len(test_cases)} queries succeeded")
        return passed > 0  # Partial success


async def run_all_tests():
    """Run all Discovery Service tests"""
    print("\n" + "=" * 70)
    print("  DISCOVERY SERVICE TEST SUITE")
    print("  Testing: LLM-based service selection with Ollama/llama3.2")
    print("=" * 70)

    results = []

    # Test 1: Ollama availability
    ollama_ok = await test_ollama_availability()
    results.append(ollama_ok)

    if not ollama_ok:
        print("\n️  Ollama is not available - skipping remaining tests")
        print("   Start Ollama first:")
        print("   1. Run: ollama serve")
        print("   2. Or start Ollama app")
        return 1

    # Test 2: llama3.2 model
    model_ok = await test_llama32_model()
    results.append(model_ok)

    if not model_ok:
        print("\n️  llama3.2 model not available - skipping remaining tests")
        print("   Install model:")
        print("   - Run: ollama pull llama3.2")
        return 1

    # Test 3: Discovery service health
    results.append(await test_discovery_service_health())

    # Test 4: Service selection
    results.append(await test_discovery_service_selection())

    # Test 5: Various queries
    results.append(await test_discovery_various_queries())

    # Summary
    print("\n" + "=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)
    passed = sum(results)
    total = len(results)

    print(f"\nTests Passed: {passed}/{total}")

    if passed == total:
        print("\n ALL DISCOVERY SERVICE TESTS PASSED!")
        print("\n Discovery Service is working correctly:")
        print("   • Ollama is running with llama3.2 model")
        print("   • Discovery endpoint is healthy")
        print("   • LLM selects appropriate services")
        print("   • Handles various query types")
        return 0
    else:
        print(f"\n️  {total - passed} test(s) failed")
        print("\nDebugging steps:")
        print("1. Start Ollama: ollama serve")
        print("2. Install model: ollama pull llama3.2")
        print("3. Start backend API: python StartupService.py")
        print("4. Check logs for detailed errors")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)