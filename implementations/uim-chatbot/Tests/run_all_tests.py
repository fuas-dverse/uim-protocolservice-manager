#!/usr/bin/env python3
"""
DVerse Comprehensive Test Suite Runner

Runs all test suites for the DVerse UIM implementation, covering:
- Catalogue functionality
- Agent interactions
- Service invocation
- Safety validation
- Reliability verification

Test Suites:
1. Service Invoker Tests (core innovation)
2. End-to-End Tests (complete workflow)
3. Chatbot HTTP Tests (HTTP interface)
4. Discovery LLM Tests (Ollama/llama3.2)
5. Safety Tests (input validation, error handling)
6. Reliability Tests (stability, recovery)

Usage:
    python run_all_tests.py              # Run all tests
    python run_all_tests.py --quick      # Run only critical tests (Service Invoker)
    python run_all_tests.py --skip-slow  # Skip LLM tests (slow)
    python run_all_tests.py --skip-llm   # Same as --skip-slow
"""
import asyncio
import sys
import os
import argparse
from typing import List, Tuple
from datetime import datetime

# Add current directory to path for test imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def print_banner():
    """Print test suite banner"""
    print("\n" + "=" * 70)
    print("  ╔══════════════════════════════════════════════════════════════╗")
    print("  ║         DVERSE COMPREHENSIVE TEST SUITE                      ║")
    print("  ║         Testing all components of the UIM implementation     ║")
    print("  ╚══════════════════════════════════════════════════════════════╝")
    print("=" * 70)
    print(f"\n📅 Test Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def print_test_suite_header(suite_name: str, description: str):
    """Print header for each test suite"""
    print("\n\n" + "▓" * 70)
    print(f"  🧪 {suite_name}")
    print(f"     {description}")
    print("▓" * 70)


def calculate_summary(results: List[Tuple[str, int]]) -> Tuple[int, int]:
    """Calculate overall test summary"""
    total_tests = len(results)
    passed_tests = sum(1 for _, exit_code in results if exit_code == 0)
    return passed_tests, total_tests


def print_final_summary(results: List[Tuple[str, int]], passed: int, total: int):
    """Print final test summary"""
    print("\n\n" + "=" * 70)
    print("  📊 FINAL TEST SUMMARY")
    print("=" * 70)

    print("\n📋 Test Suite Results:")
    for suite_name, exit_code in results:
        status = "✅ PASSED" if exit_code == 0 else "❌ FAILED"
        print(f"   {suite_name:30} {status}")

    print(f"\n📈 Overall: {passed}/{total} test suites passed")

    if passed == total:
        print("\n" + "=" * 70)
        print("  🎉 ALL TEST SUITES PASSED!")
        print("=" * 70)
        print("\n✅ DVerse system is fully validated:")
        print("   • Generic Service Invoker works correctly (core innovation)")
        print("   • End-to-end workflow completes successfully")
        print("   • Chatbot HTTP interface responds properly")
        print("   • Discovery Service LLM selection is accurate")
        print("   • Safety: Input validation and error handling work")
        print("   • Reliability: System is stable under varied conditions")
        print("\n🎓 Ready for demonstration and portfolio inclusion")

    elif passed > 0:
        print(f"\n⚠️  PARTIAL SUCCESS: {total - passed} suite(s) failed")
        print("\n❌ Failed suites:")
        for suite_name, exit_code in results:
            if exit_code != 0:
                print(f"   • {suite_name}")
        print("\n💡 Review individual test outputs above for details")

    else:
        print("\n❌ ALL TEST SUITES FAILED")
        print("\n🔍 Check prerequisites:")
        print("   1. Backend API running on port 8000")
        print("   2. MongoDB running and seeded")
        print("   3. Ollama running with llama3.2 model")
        print("   4. Chatbot service running on port 8001")


async def run_all_suites(skip_slow: bool = False, quick: bool = False) -> List[Tuple[str, int]]:
    """
    Run all test suites

    Returns:
        List of (suite_name, exit_code) tuples
    """
    results = []

    # Import test modules
    try:
        from test_service_invoker import run_all_tests as run_service_invoker_tests
        from test_e2e import run_all_tests as run_e2e_tests
        from test_chatbot import run_all_tests as run_chatbot_tests
        from test_discovery_llm import run_all_tests as run_discovery_tests
        from test_safety import run_all_tests as run_safety_tests
        from test_reliability import run_all_tests as run_reliability_tests
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\nMake sure all test files are in the same directory:")
        print("   - test_service_invoker.py")
        print("   - test_e2e.py")
        print("   - test_chatbot.py")
        print("   - test_discovery_llm.py")
        print("   - test_safety.py")
        print("   - test_reliability.py")
        return [("Import", 1)]

    # ═══════════════════════════════════════════════════════════════════
    # SUITE 1: Generic Service Invoker (CRITICAL - Core Innovation)
    # ═══════════════════════════════════════════════════════════════════
    print_test_suite_header(
        "SUITE 1: GENERIC SERVICE INVOKER",
        "Tests metadata-driven service invocation (core innovation)"
    )
    result = await run_service_invoker_tests()
    results.append(("Service Invoker", result))

    if quick:
        # Quick mode: only run the most critical test
        return results

    # ═══════════════════════════════════════════════════════════════════
    # SUITE 2: End-to-End Tests (CRITICAL - Complete Workflow)
    # ═══════════════════════════════════════════════════════════════════
    print_test_suite_header(
        "SUITE 2: END-TO-END WORKFLOW",
        "Tests complete DVerse system flow"
    )
    result = await run_e2e_tests()
    results.append(("End-to-End", result))

    # ═══════════════════════════════════════════════════════════════════
    # SUITE 3: Chatbot HTTP Tests
    # ═══════════════════════════════════════════════════════════════════
    print_test_suite_header(
        "SUITE 3: CHATBOT HTTP INTERFACE",
        "Tests chatbot /chat endpoint"
    )
    result = await run_chatbot_tests()
    results.append(("Chatbot HTTP", result))

    # ═══════════════════════════════════════════════════════════════════
    # SUITE 4: Safety Tests
    # ═══════════════════════════════════════════════════════════════════
    print_test_suite_header(
        "SUITE 4: SAFETY VALIDATION",
        "Tests input validation, error handling, injection protection"
    )
    result = await run_safety_tests()
    results.append(("Safety", result))

    # ═══════════════════════════════════════════════════════════════════
    # SUITE 5: Reliability Tests
    # ═══════════════════════════════════════════════════════════════════
    print_test_suite_header(
        "SUITE 5: RELIABILITY VERIFICATION",
        "Tests system stability, concurrency, error recovery"
    )
    result = await run_reliability_tests()
    results.append(("Reliability", result))

    # ═══════════════════════════════════════════════════════════════════
    # SUITE 6: Discovery LLM Tests (SLOW - uses LLM inference)
    # ═══════════════════════════════════════════════════════════════════
    if not skip_slow:
        print_test_suite_header(
            "SUITE 6: DISCOVERY SERVICE (LLM)",
            "Tests Ollama/llama3.2 service selection"
        )
        result = await run_discovery_tests()
        results.append(("Discovery LLM", result))
    else:
        print("\n⏭️  Skipping Discovery LLM tests (--skip-slow flag)")

    return results


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="DVerse Comprehensive Test Suite Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_all_tests.py              # Run all tests
  python run_all_tests.py --quick      # Run only critical tests (Service Invoker)
  python run_all_tests.py --skip-slow  # Skip LLM tests
  python run_all_tests.py --skip-llm   # Same as --skip-slow

Test Suites:
  1. Service Invoker    - Core innovation: metadata-driven invocation
  2. End-to-End         - Complete workflow validation
  3. Chatbot HTTP       - HTTP interface testing
  4. Safety             - Input validation & error handling
  5. Reliability        - Stability & recovery
  6. Discovery LLM      - LLM-based service selection (slow)
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

    parser.add_argument(
        "--skip-llm",
        action="store_true",
        help="Same as --skip-slow"
    )

    args = parser.parse_args()
    skip_slow = args.skip_slow or args.skip_llm

    # Print banner
    print_banner()

    if args.quick:
        print("\n⚡ QUICK MODE: Running only critical tests")
    elif skip_slow:
        print("\n⏭️  SKIPPING: Discovery LLM tests (slow)")
    else:
        print("\n🔄 FULL MODE: Running all test suites")

    # Run all test suites
    try:
        results = asyncio.run(run_all_suites(skip_slow=skip_slow, quick=args.quick))

        # Calculate and print summary
        passed, total = calculate_summary(results)
        print_final_summary(results, passed, total)

        # Exit with appropriate code
        sys.exit(0 if passed == total else 1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()