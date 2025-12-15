#!/usr/bin/env python3
"""
DVerse Test Suite Runner

Runs all test suites for the DVerse UIM implementation.

Test Suites:
1. Service Invoker Tests (core innovation)
2. End-to-End Tests (complete workflow)
3. Chatbot HTTP Tests (HTTP interface)
4. Discovery LLM Tests (Ollama/llama3.2)

Usage:
    python run_all_tests.py              # Run all tests
    python run_all_tests.py --quick      # Run only critical tests
    python run_all_tests.py --skip-slow  # Skip LLM tests (slow)
"""
import asyncio
import sys
import os
import argparse
from typing import List, Tuple

# Add parent directory to path for test imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test suite imports
try:
    from test_service_invoker import run_all_tests as run_service_invoker_tests
    from test_e2e import run_all_tests as run_e2e_tests
    from test_chatbot import run_all_tests as run_chatbot_tests
    from test_discovery_llm import run_all_tests as run_discovery_tests
except ImportError as e:
    print(f" Import error: {e}")
    print("Make sure you're running this from the Tests directory")
    print(f"Current directory: {os.getcwd()}")
    print(f"Expected location: implementations/uim-chatbot/Tests/")
    sys.exit(1)


def print_banner():
    """Print test suite banner"""
    print("\n" + "=" * 70)
    print("  DVERSE COMPREHENSIVE TEST SUITE")
    print("  Testing all components of the DVerse UIM implementation")
    print("=" * 70)


def print_test_suite_header(suite_name: str, description: str):
    """Print header for each test suite"""
    print("\n\n" + "" * 35)
    print(f"  {suite_name}")
    print(f"  {description}")
    print("" * 35)


async def run_all_suites(skip_slow: bool = False, quick: bool = False) -> Tuple[int, int]:
    """
    Run all test suites

    Returns:
        Tuple of (total_passed, total_tests)
    """
    results = []

    # 1. Service Invoker Tests (CRITICAL - Core Innovation)
    print_test_suite_header(
        "SUITE 1: GENERIC SERVICE INVOKER",
        "Tests metadata-driven service invocation (core innovation)"
    )
    result = await run_service_invoker_tests()
    results.append(("Service Invoker", result))

    if quick:
        # Quick mode: only run critical tests
        return calculate_summary(results)

    # 2. End-to-End Tests (CRITICAL - Complete Workflow)
    print_test_suite_header(
        "SUITE 2: END-TO-END WORKFLOW",
        "Tests complete DVerse system flow"
    )
    result = await run_e2e_tests()
    results.append(("End-to-End", result))

    # 3. Chatbot HTTP Tests
    print_test_suite_header(
        "SUITE 3: CHATBOT HTTP INTERFACE",
        "Tests chatbot /chat endpoint"
    )
    result = await run_chatbot_tests()
    results.append(("Chatbot HTTP", result))

    if not skip_slow:
        # 4. Discovery LLM Tests (SLOW - uses LLM inference)
        print_test_suite_header(
            "SUITE 4: DISCOVERY SERVICE (LLM)",
            "Tests Ollama/llama3.2 service selection"
        )
        result = await run_discovery_tests()
        results.append(("Discovery LLM", result))
    else:
        print("\n Skipping Discovery LLM tests (--skip-slow flag)")

    return calculate_summary(results)


def calculate_summary(results: List[Tuple[str, int]]) -> Tuple[int, int]:
    """Calculate overall test summary"""
    total_tests = len(results)
    passed_tests = sum(1 for _, exit_code in results if exit_code == 0)

    return passed_tests, total_tests


def print_final_summary(results: List[Tuple[str, int]], passed: int, total: int):
    """Print final test summary"""
    print("\n\n" + "=" * 70)
    print("  FINAL TEST SUMMARY")
    print("=" * 70)

    print("\n Test Suite Results:")
    for suite_name, exit_code in results:
        status = " PASSED" if exit_code == 0 else " FAILED"
        print(f"   {suite_name:25} {status}")

    print(f"\n Overall: {passed}/{total} test suites passed")

    if passed == total:
        print("\n ALL TEST SUITES PASSED!")
        print("\n DVerse system is fully validated:")
        print("   • Generic Service Invoker works correctly")
        print("   • End-to-end workflow completes successfully")
        print("   • Chatbot HTTP interface responds properly")
        if any("Discovery" in name for name, _ in results):
            print("   • Discovery Service LLM selection is accurate")

        print("\n Ready for demonstration and portfolio inclusion")

    elif passed > 0:
        print(f"\n️  PARTIAL SUCCESS: {total - passed} suite(s) failed")
        print("\nFailed suites:")
        for suite_name, exit_code in results:
            if exit_code != 0:
                print(f"   • {suite_name}")

        print("\n Review individual test outputs above for details")

    else:
        print("\n ALL TEST SUITES FAILED")
        print("\n Check prerequisites:")
        print("   1. Backend API running on port 8000")
        print("   2. MongoDB running and seeded")
        print("   3. Ollama running with llama3.2 model")
        print("   4. Chatbot service running on port 8001")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="DVerse Comprehensive Test Suite Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_all_tests.py              # Run all tests
  python run_all_tests.py --quick      # Run only critical tests
  python run_all_tests.py --skip-slow  # Skip LLM tests
        """
    )

    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run only critical tests (Service Invoker only)"
    )

    parser.add_argument(
        "--skip-slow",
        action="store_true",
        help="Skip slow tests (Discovery LLM tests)"
    )

    args = parser.parse_args()

    # Print banner
    print_banner()

    if args.quick:
        print("\n QUICK MODE: Running only critical tests")
    elif args.skip_slow:
        print("\n SKIPPING: Discovery LLM tests (slow)")
    else:
        print("\n FULL MODE: Running all test suites")

    # Run all test suites
    try:
        results = []

        # Run tests
        if args.quick:
            # Quick mode: only service invoker
            print_test_suite_header(
                "SUITE 1: GENERIC SERVICE INVOKER",
                "Tests metadata-driven service invocation (core innovation)"
            )
            result = asyncio.run(run_service_invoker_tests())
            results.append(("Service Invoker", result))
        else:
            # Full test suite
            passed, total = asyncio.run(run_all_suites(skip_slow=args.skip_slow))

            # Rebuild results list for summary
            # (This is a hack because run_all_suites already prints everything)
            # In a real implementation, we'd refactor to separate execution and reporting
            results = [("All Suites", 0 if passed == total else 1)]

        # Print final summary
        passed = sum(1 for _, code in results if code == 0)
        total = len(results)
        print_final_summary(results, passed, total)

        # Exit with appropriate code
        sys.exit(0 if passed == total else 1)

    except KeyboardInterrupt:
        print("\n\n️  Tests interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()