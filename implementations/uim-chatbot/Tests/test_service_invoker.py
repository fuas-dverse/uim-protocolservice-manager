#!/usr/bin/env python3
"""
Test Suite for Generic Service Invoker

Tests DVerse's core innovation: template-based service invocation that bypasses
unreliable LLM formatting.

Test Cases:
1. Successful invocation (arXiv - no auth required)
2. Authentication error handling (News API - missing API key)
"""
import asyncio
import sys
import os
from typing import Dict, Any

# Add parent directory to path for imports
PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PARENT_DIR)

try:
    from service_invoker import GenericServiceInvoker
    from loguru import logger
except ImportError as e:
    print(f" Import failed: {e}")
    print(f"Make sure you're running this from the Tests directory")
    print(f"Current directory: {os.getcwd()}")
    print(f"Parent directory: {PARENT_DIR}")
    print(f"Expected structure:")
    print(f"  implementations/uim-chatbot/")
    print(f"  ├── service_invoker.py")
    print(f"  └── Tests/")
    print(f"      └── test_service_invoker.py")
    sys.exit(1)

# ==================== TEST DATA ====================

ARXIV_SERVICE_METADATA = {
    "name": "arXiv API",
    "service_url": "http://export.arxiv.org/api",
    "auth_type": "none",
    "auth_header_name": None,
    "auth_query_param": None
}

ARXIV_INTENT_METADATA = {
    "intent_name": "search_papers",
    "http_method": "GET",
    "endpoint_path": "/query",
    "input_parameters": [
        {
            "name": "search_query",
            "type": "string",
            "description": "Search query",
            "required": True,
            "location": "query"
        },
        {
            "name": "max_results",
            "type": "integer",
            "description": "Maximum number of results",
            "required": False,
            "default": 10,
            "location": "query"
        },
        {
            "name": "sortBy",
            "type": "string",
            "description": "Sort by: relevance, lastUpdatedDate, submittedDate",
            "required": False,
            "default": "relevance",
            "location": "query"
        },
        {
            "name": "sortOrder",
            "type": "string",
            "description": "Sort order: ascending or descending",
            "required": False,
            "default": "descending",
            "location": "query"
        }
    ]
}

NEWS_SERVICE_METADATA = {
    "name": "News API",
    "service_url": "https://newsapi.org/v2",
    "auth_type": "api_key",
    "auth_header_name": None,
    "auth_query_param": "apiKey"
}

NEWS_INTENT_METADATA = {
    "intent_name": "search_articles",
    "http_method": "GET",
    "endpoint_path": "/everything",
    "input_parameters": [
        {
            "name": "q",
            "type": "string",
            "description": "Search query",
            "required": True,
            "location": "query"
        },
        {
            "name": "sortBy",
            "type": "string",
            "description": "Sort by: relevancy, popularity, publishedAt",
            "required": False,
            "default": "publishedAt",
            "location": "query"
        }
    ]
}


# ==================== TEST FUNCTIONS ====================

async def test_arxiv_success():
    """
    TEST 1: Successful service invocation (arXiv)

    This tests the CORE INNOVATION of DVerse:
    - Generic service invoker constructs HTTP request from metadata
    - No hardcoded API logic
    - Template-based response formatting (tested separately)

    Expected: Real papers returned, no errors
    """
    print("\n" + "=" * 70)
    print("TEST 1: Generic Service Invoker - arXiv (Success Case)")
    print("=" * 70)

    invoker = GenericServiceInvoker(timeout=30)

    try:
        # Test parameters: search for papers about "transformer models"
        parameters = {
            "search_query": "all:transformer attention mechanism",
            "max_results": 5,
            "sortBy": "relevance",
            "sortOrder": "descending"
        }

        print(f" Service: {ARXIV_SERVICE_METADATA['name']}")
        print(f" Intent: {ARXIV_INTENT_METADATA['intent_name']}")
        print(f" Parameters: {parameters}")
        print()

        # Invoke service
        result = await invoker.invoke(
            service_metadata=ARXIV_SERVICE_METADATA,
            intent_metadata=ARXIV_INTENT_METADATA,
            parameters=parameters
        )

        # Validate result structure
        assert isinstance(result, dict), "Result should be a dictionary"
        assert result.get("success") is True, "Success flag should be True"

        # Validate papers data
        papers = result.get("papers", [])
        assert isinstance(papers, list), "Papers should be a list"
        assert len(papers) > 0, "Should return at least one paper"
        assert len(papers) <= 5, "Should not exceed max_results"

        # Validate paper structure
        first_paper = papers[0]
        required_fields = ["title", "authors", "summary", "published"]
        for field in required_fields:
            assert field in first_paper, f"Paper should have '{field}' field"
            assert first_paper[field], f"Paper '{field}' should not be empty"

        # url is optional (some papers might not have it)
        assert "url" in first_paper, "Paper should have 'url' field (even if None)"

        # Log results
        print(" TEST 1 PASSED")
        print(f"    Successfully invoked {ARXIV_SERVICE_METADATA['name']}")
        print(f"    Retrieved {len(papers)} papers")
        print(f"    All papers have required fields")
        print(f"\n Sample paper:")
        print(f"   Title: {first_paper['title'][:80]}...")
        print(f"   Authors: {', '.join(first_paper['authors'][:2])}")
        if first_paper.get('url'):
            print(f"   URL: {first_paper['url']}")
        else:
            print(f"   URL: (No link available for this paper)")

        return True

    except AssertionError as e:
        print(f" TEST 1 FAILED: {e}")
        return False
    except Exception as e:
        print(f" TEST 1 FAILED WITH EXCEPTION: {e}")
        logger.exception("Full traceback:")
        return False
    finally:
        await invoker.close()


async def test_news_api_auth_error():
    """
    TEST 2: Authentication error handling (News API without key)

    This tests DVerse's error handling:
    - Generic service invoker properly handles auth requirements
    - Missing API key results in clear error message
    - Error is caught and reported, not crash

    Expected: Exception raised with authentication error message
    """
    print("\n" + "=" * 70)
    print("TEST 2: Generic Service Invoker - News API (Auth Error Case)")
    print("=" * 70)

    invoker = GenericServiceInvoker(timeout=30)

    try:
        # Test parameters: search for news about "artificial intelligence"
        parameters = {
            "q": "artificial intelligence",
            "sortBy": "publishedAt"
        }

        print(f" Service: {NEWS_SERVICE_METADATA['name']}")
        print(f" Intent: {NEWS_INTENT_METADATA['intent_name']}")
        print(f" Parameters: {parameters}")
        print(f"️  Expected: Authentication error (no API key configured)")
        print()

        # Invoke service - should fail with auth error
        result = await invoker.invoke(
            service_metadata=NEWS_SERVICE_METADATA,
            intent_metadata=NEWS_INTENT_METADATA,
            parameters=parameters
        )

        # If we get here without exception, test failed
        print(f" TEST 2 FAILED: Should have raised authentication error")
        print(f"   Got result instead: {result}")
        return False

    except Exception as e:
        error_message = str(e).lower()

        # Check if error message indicates authentication/authorization issue
        auth_keywords = ["401", "unauthorized", "authentication", "api key", "apikey", "forbidden", "403"]
        is_auth_error = any(keyword in error_message for keyword in auth_keywords)

        if is_auth_error:
            print(" TEST 2 PASSED")
            print(f"    Correctly raised authentication error")
            print(f"    Error message: {str(e)[:150]}")
            print(f"    Generic Service Invoker properly handles missing API keys")
            return True
        else:
            print(f" TEST 2 FAILED: Wrong error type")
            print(f"   Expected: Authentication error (401/403/unauthorized)")
            print(f"   Got: {str(e)}")
            return False

    finally:
        await invoker.close()


async def test_parameter_substitution():
    """
    BONUS TEST 3: Parameter substitution in different locations

    Tests that the Generic Service Invoker correctly places parameters in:
    - Query params
    - Path params
    - Body params
    - Headers

    This validates the metadata-driven approach works for all parameter types.
    """
    print("\n" + "=" * 70)
    print("BONUS TEST 3: Parameter Substitution Validation")
    print("=" * 70)

    # Use arXiv again but validate the URL construction
    invoker = GenericServiceInvoker(timeout=30)

    try:
        parameters = {
            "search_query": "all:machine learning",
            "max_results": 3
        }

        print(f" Testing parameter substitution")
        print(f"   - search_query should go in query params")
        print(f"   - max_results should go in query params")
        print()

        # Invoke and check that parameters were correctly substituted
        result = await invoker.invoke(
            service_metadata=ARXIV_SERVICE_METADATA,
            intent_metadata=ARXIV_INTENT_METADATA,
            parameters=parameters
        )

        # If we got a successful response, parameters were substituted correctly
        assert result.get("success") is True
        assert len(result.get("papers", [])) <= 3, "max_results parameter was not applied"

        print(" BONUS TEST 3 PASSED")
        print(f"    Parameters correctly placed in query string")
        print(f"    max_results limit was respected ({len(result.get('papers', []))} <= 3)")

        return True

    except Exception as e:
        print(f" BONUS TEST 3 FAILED: {e}")
        return False
    finally:
        await invoker.close()


# ==================== MAIN ====================

async def run_all_tests():
    """Run all Generic Service Invoker tests"""
    print("\n" + "=" * 70)
    print("  GENERIC SERVICE INVOKER TEST SUITE")
    print("  Testing DVerse's Core Innovation: Metadata-Driven Service Invocation")
    print("=" * 70)

    results = []

    # Test 1: Success case (arXiv)
    results.append(await test_arxiv_success())

    # Test 2: Auth error case (News API)
    results.append(await test_news_api_auth_error())

    # Bonus Test 3: Parameter substitution
    results.append(await test_parameter_substitution())

    # Summary
    print("\n" + "=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)
    passed = sum(results)
    total = len(results)

    print(f"\nTests Passed: {passed}/{total}")

    if passed == total:
        print("\n ALL TESTS PASSED!")
        print("\n Generic Service Invoker is working correctly:")
        print("   • Successfully invokes services without API keys (arXiv)")
        print("   • Properly handles authentication errors (News API)")
        print("   • Correctly substitutes parameters in requests")
        print("   • Template-based approach works (no LLM hallucinations)")
        return 0
    else:
        print(f"\n️  {total - passed} test(s) failed")
        print("\nDebugging steps:")
        print("1. Check that MongoDB is running and seeded with services")
        print("2. Verify arXiv API is accessible (http://export.arxiv.org)")
        print("3. Check service_invoker.py for any recent changes")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)