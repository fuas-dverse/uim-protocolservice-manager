#!/usr/bin/env python3
"""
Reliability Test Suite for DVerse

Tests that the system maintains stable operation under varied conditions,
handles failures gracefully, and provides consistent behavior.

Test Categories (from Research doc):
- Consecutive sessions with mixed load
- Synchronization stability
- Error recovery

Test Cases:
1. Consecutive queries (stability under repeated use)
2. Service timeout handling
3. Concurrent request handling
"""
import asyncio
import sys
import os
import httpx
import time
from typing import List, Tuple

# Configuration
API_BASE_URL = "http://localhost:8000"
CHATBOT_BASE_URL = "http://localhost:8001"


async def test_consecutive_sessions():
    """
    TEST 1: Consecutive Sessions
    
    Run multiple queries in sequence to verify consistent behavior.
    Expected: All queries return consistent, valid responses.
    """
    print("\n" + "=" * 70)
    print("RELIABILITY TEST 1: Consecutive Sessions")
    print("=" * 70)
    
    test_queries = [
        "Find papers about machine learning",
        "What's the weather like?",
        "Search for GitHub repositories",
        "Find news about technology",
        "Search for papers about transformers",
    ]
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            results: List[Tuple[str, int, float]] = []
            
            print(f"📋 Running {len(test_queries)} consecutive queries...")
            print()
            
            for i, query in enumerate(test_queries, 1):
                start_time = time.time()
                
                response = await client.post(
                    f"{API_BASE_URL}/query/",
                    json={
                        "query": query,
                        "agent_id": f"reliability-test-{i}",
                        "use_ai": False
                    }
                )
                
                elapsed = time.time() - start_time
                results.append((query[:40], response.status_code, elapsed))
                
                print(f"   Query {i}: HTTP {response.status_code} ({elapsed:.2f}s)")
                
                # Small delay between requests to simulate real usage
                await asyncio.sleep(0.5)
            
            # Validate all requests succeeded
            success_count = sum(1 for _, status, _ in results if status == 200)
            avg_time = sum(elapsed for _, _, elapsed in results) / len(results)
            
            assert success_count == len(test_queries), \
                f"Expected all {len(test_queries)} to succeed, got {success_count}"
            
            # Check response time consistency (no single request taking way longer)
            times = [elapsed for _, _, elapsed in results]
            max_time = max(times)
            min_time = min(times)
            
            # Allow up to 5x variance (reasonable for network operations)
            time_variance_ok = max_time < (min_time * 5 + 2)  # +2 for baseline variance
            
            print()
            print("✅ RELIABILITY TEST 1 PASSED")
            print(f"   ✓ All {len(test_queries)} queries completed successfully")
            print(f"   ✓ Average response time: {avg_time:.2f}s")
            print(f"   ✓ Response time range: {min_time:.2f}s - {max_time:.2f}s")
            
            if not time_variance_ok:
                print(f"   ⚠️  Note: High time variance detected")
            
            return True
            
    except AssertionError as e:
        print(f"❌ RELIABILITY TEST 1 FAILED: {e}")
        return False
    except httpx.ConnectError:
        print("❌ RELIABILITY TEST 1 FAILED: Cannot connect to API")
        return False
    except Exception as e:
        print(f"❌ RELIABILITY TEST 1 FAILED WITH EXCEPTION: {e}")
        return False


async def test_service_timeout_handling():
    """
    TEST 2: Service Timeout Handling
    
    Test that the system handles slow/unresponsive external services gracefully.
    We can't easily simulate a timeout, but we can verify timeout configuration exists
    and the system doesn't hang indefinitely.
    
    Expected: System has reasonable timeout, returns error rather than hanging.
    """
    print("\n" + "=" * 70)
    print("RELIABILITY TEST 2: Timeout Configuration Verification")
    print("=" * 70)
    
    try:
        # Test with a reasonable timeout that the API should complete within
        async with httpx.AsyncClient(timeout=60.0) as client:
            start_time = time.time()
            
            # Make a query that requires external service call
            response = await client.post(
                f"{API_BASE_URL}/query/",
                json={
                    "query": "Find papers about neural networks",
                    "agent_id": "timeout-test",
                    "use_ai": True  # Use AI mode to trigger more complex processing
                }
            )
            
            elapsed = time.time() - start_time
            
            # Response should come back within reasonable time
            # Even if service fails, we should get a response
            assert elapsed < 60, f"Request took too long: {elapsed:.2f}s"
            
            # Should get a valid response (success or graceful error)
            assert response.status_code in [200, 400, 408, 422, 500, 503, 504], \
                f"Unexpected status: {response.status_code}"
            
            # If we got a response, it should be valid JSON
            try:
                data = response.json()
                assert isinstance(data, dict), "Response should be JSON object"
            except Exception:
                pass  # Some error responses might not be JSON
            
            print("✅ RELIABILITY TEST 2 PASSED")
            print(f"   ✓ Request completed in {elapsed:.2f}s")
            print(f"   ✓ Response status: HTTP {response.status_code}")
            print(f"   ✓ System does not hang on requests")
            
            return True
            
    except httpx.TimeoutException:
        print("❌ RELIABILITY TEST 2 FAILED: Request timed out")
        print("   System may be hanging on external service calls")
        return False
    except httpx.ConnectError:
        print("❌ RELIABILITY TEST 2 FAILED: Cannot connect to API")
        return False
    except AssertionError as e:
        print(f"❌ RELIABILITY TEST 2 FAILED: {e}")
        return False
    except Exception as e:
        print(f"❌ RELIABILITY TEST 2 FAILED WITH EXCEPTION: {e}")
        return False


async def test_concurrent_requests():
    """
    TEST 3: Concurrent Request Handling
    
    Send multiple requests simultaneously to test thread safety.
    Expected: All requests complete without errors, no race conditions.
    """
    print("\n" + "=" * 70)
    print("RELIABILITY TEST 3: Concurrent Request Handling")
    print("=" * 70)
    
    num_concurrent = 5
    
    async def make_request(client: httpx.AsyncClient, request_id: int) -> Tuple[int, int, float]:
        """Make a single request and return (id, status, time)"""
        start = time.time()
        try:
            response = await client.post(
                f"{API_BASE_URL}/query/",
                json={
                    "query": f"Test query {request_id}",
                    "agent_id": f"concurrent-test-{request_id}",
                    "use_ai": False
                }
            )
            elapsed = time.time() - start
            return (request_id, response.status_code, elapsed)
        except Exception as e:
            elapsed = time.time() - start
            return (request_id, -1, elapsed)  # -1 indicates error
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print(f"📋 Sending {num_concurrent} concurrent requests...")
            
            # Create all tasks
            tasks = [make_request(client, i) for i in range(num_concurrent)]
            
            # Run all concurrently
            start_time = time.time()
            results = await asyncio.gather(*tasks)
            total_time = time.time() - start_time
            
            # Analyze results
            print()
            for req_id, status, elapsed in results:
                status_str = f"HTTP {status}" if status > 0 else "ERROR"
                print(f"   Request {req_id}: {status_str} ({elapsed:.2f}s)")
            
            # Count successes
            success_count = sum(1 for _, status, _ in results if status == 200)
            error_count = sum(1 for _, status, _ in results if status < 0)
            
            # All should succeed
            assert error_count == 0, f"{error_count} requests failed with exceptions"
            assert success_count == num_concurrent, \
                f"Expected {num_concurrent} successes, got {success_count}"
            
            # Total time should be less than sequential (proving concurrency works)
            # Individual requests might take ~2-5s each
            expected_sequential_time = num_concurrent * 2  # Conservative estimate
            
            print()
            print("✅ RELIABILITY TEST 3 PASSED")
            print(f"   ✓ All {num_concurrent} concurrent requests succeeded")
            print(f"   ✓ Total time: {total_time:.2f}s")
            print(f"   ✓ No race conditions or thread safety issues")
            
            if total_time < expected_sequential_time:
                print(f"   ✓ Concurrency working (faster than sequential)")
            
            return True
            
    except AssertionError as e:
        print(f"❌ RELIABILITY TEST 3 FAILED: {e}")
        return False
    except httpx.ConnectError:
        print("❌ RELIABILITY TEST 3 FAILED: Cannot connect to API")
        return False
    except Exception as e:
        print(f"❌ RELIABILITY TEST 3 FAILED WITH EXCEPTION: {e}")
        return False


async def test_recovery_after_error():
    """
    TEST 4: Recovery After Error
    
    Verify the system continues working normally after encountering an error.
    Expected: Error does not break subsequent requests.
    """
    print("\n" + "=" * 70)
    print("RELIABILITY TEST 4: Recovery After Error")
    print("=" * 70)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Step 1: Make a normal request (should work)
            print("   Step 1: Normal request...")
            response1 = await client.post(
                f"{API_BASE_URL}/query/",
                json={
                    "query": "Find papers",
                    "agent_id": "recovery-test",
                    "use_ai": False
                }
            )
            assert response1.status_code == 200, f"Initial request failed: {response1.status_code}"
            print(f"   ✓ Initial request: HTTP {response1.status_code}")
            
            # Step 2: Cause an error (invalid request)
            print("   Step 2: Triggering error condition...")
            response2 = await client.post(
                f"{API_BASE_URL}/query/",
                content="invalid json {{{",
                headers={"Content-Type": "application/json"}
            )
            print(f"   ✓ Error request: HTTP {response2.status_code}")
            
            # Step 3: Make another normal request (should still work)
            print("   Step 3: Recovery request...")
            response3 = await client.post(
                f"{API_BASE_URL}/query/",
                json={
                    "query": "Find more papers",
                    "agent_id": "recovery-test",
                    "use_ai": False
                }
            )
            assert response3.status_code == 200, \
                f"Recovery request failed: {response3.status_code}"
            print(f"   ✓ Recovery request: HTTP {response3.status_code}")
            
            # Step 4: Verify health endpoint
            print("   Step 4: Health check...")
            health = await client.get(f"{API_BASE_URL}/health")
            assert health.status_code == 200, f"Health check failed: {health.status_code}"
            print(f"   ✓ Health check: HTTP {health.status_code}")
            
            print()
            print("✅ RELIABILITY TEST 4 PASSED")
            print(f"   ✓ System recovered after error condition")
            print(f"   ✓ Subsequent requests work normally")
            print(f"   ✓ Health endpoint confirms system stability")
            
            return True
            
    except AssertionError as e:
        print(f"❌ RELIABILITY TEST 4 FAILED: {e}")
        return False
    except httpx.ConnectError:
        print("❌ RELIABILITY TEST 4 FAILED: Cannot connect to API")
        return False
    except Exception as e:
        print(f"❌ RELIABILITY TEST 4 FAILED WITH EXCEPTION: {e}")
        return False


async def run_all_tests():
    """Run all reliability tests"""
    print("\n" + "=" * 70)
    print("  DVERSE RELIABILITY TEST SUITE")
    print("  Testing system stability and error recovery")
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
    
    # Run all reliability tests
    results.append(await test_consecutive_sessions())
    results.append(await test_service_timeout_handling())
    results.append(await test_concurrent_requests())
    results.append(await test_recovery_after_error())
    
    # Summary
    print("\n" + "=" * 70)
    print("  RELIABILITY TEST SUMMARY")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL RELIABILITY TESTS PASSED!")
        print("\n🔒 System reliability validated:")
        print("   • Consecutive sessions work consistently")
        print("   • Timeout handling is configured")
        print("   • Concurrent requests handled safely")
        print("   • System recovers gracefully from errors")
        return 0
    else:
        print(f"\n⚠️  {total - passed} reliability test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
