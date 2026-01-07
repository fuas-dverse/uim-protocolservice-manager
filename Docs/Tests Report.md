# DVerse UIM Prototype

Test Reports

**Author:** Rik Heerholtz

**Date:** 06/01/2026

**Version:** 1.0

**Project:** DVerse Research Program - Fontys ICT

# Executive Summary

This document presents the testing results for the DVerse UIM (Unified Intent Mediator) prototype, validating catalogue functionality, agent interactions, and service invocation. The test suites cover the core system components and demonstrate system performance and reliability.

Testing was conducted across seven test suites covering API endpoints, the Generic Service Invoker (core innovation), end-to-end workflows, chatbot interface, LLM-based discovery, safety validation, and reliability verification.

## Test Suite Summary

| **Test Suite** | **Tests** | **Passed** | **Status** |
| --- | --- | --- | --- |
| API Endpoint Tests | 7   | \[7/7\] | **PASSED** |
| Generic Service Invoker | 3   | \[3/3\] | **PASSED** |
| End-to-End Workflow | 5   | \[5/5\] | **PASSED** |
| Chatbot HTTP Interface | 5   | \[5/5\] | **PASSED** |
| Discovery Service (LLM) | 5   | \[5/5\] | **PASSED** |
| Safety Tests | 3   | \[3/3\] | **PASSED** |
| Reliability Tests | 4   | \[4/4\] | **PASSED** |

**Total: \[32/32\] tests passed**

# 1\. Catalogue Functionality Tests

These tests validate the Backend API endpoints that provide access to the service catalogue, including service retrieval, intent queries, and the unified query interface.

## 1.1 API Endpoint Tests

**Test File:** _test_API.py_

| **Test Name** | **Description** | **Expected** | **Status** |
| --- | --- | --- | --- |
| **Root Endpoint** | GET / returns API info | HTTP 200 | **PASSED** |
| **Health Check** | GET /health returns status | HTTP 200 | **PASSED** |
| **Get All Services** | GET /services returns catalogue | HTTP 200, list of services | **PASSED** |
| **Get All Intents** | GET /intents returns all intents | HTTP 200, list of intents | **PASSED** |
| **Query (Keyword)** | POST /query/ with keyword search | HTTP 200, matching services | **PASSED** |
| **Query Health** | GET /query/health check | HTTP 200 | **PASSED** |
| **API Documentation** | GET /docs returns Swagger UI | HTTP 200 | **PASSED** |

# 2\. Service Invocation Tests

These tests validate the Generic Service Invoker, the core innovation of DVerse. The invoker uses metadata-driven HTTP request construction to call any UIM-compliant service without hardcoded API logic.

## 2.1 Generic Service Invoker Tests

**Test File:** _test_service_invoker.py_

| **Test Name** | **Description** | **Expected** | **Status** |
| --- | --- | --- | --- |
| **arXiv Success** | Invoke arXiv API via metadata-driven approach | Returns papers, success=true | **PASSED** |
| **News API Auth Error** | Invoke News API without key | 401/403 error handled gracefully | **PASSED** |
| **Parameter Substitution** | Parameters placed in correct locations | max_results respected | **PASSED** |

### Key Validation Points

The Generic Service Invoker demonstrates metadata-driven invocation by reading endpoint paths, HTTP methods, and parameter locations from service/intent metadata rather than hardcoded logic. This enables the system to invoke any registered service without code changes.

# 3\. Agent Interaction Tests

These tests validate the complete agent interaction workflow, from natural language query processing through LLM-based service discovery to formatted response delivery.

## 3.1 End-to-End Workflow Tests

**Test File:** _test_e2e.py_

| **Test Name** | **Description** | **Expected** | **Status** |
| --- | --- | --- | --- |
| **Discovery Service** | LLM selects appropriate service for query | Returns service metadata | **PASSED** |
| **Full Workflow (arXiv)** | Query > Discovery > Invocation > Format | Structured response with papers | **PASSED** |
| **Auth Error Handling** | News API workflow with missing key | Graceful error message | **PASSED** |
| **Database Performance** | N+1 query fix validation | Response < 5 seconds | **PASSED** |
| **Template Formatting** | Deterministic output, no hallucinations | Consistent formatting | **PASSED** |

## 3.2 Chatbot HTTP Interface Tests

**Test File:** _test_chatbot.py_

| **Test Name** | **Description** | **Expected** | **Status** |
| --- | --- | --- | --- |
| **Health Check** | GET / health endpoint | HTTP 200 | **PASSED** |
| **Discover Endpoint** | POST /chat/discover service selection | Returns service_name, intent_name | **PASSED** |
| **Invoke Endpoint** | POST /chat/invoke full flow | Formatted response with papers | **PASSED** |
| **Auth Error Handling** | Handle missing API key gracefully | Graceful error response | **PASSED** |
| **Response Format** | Validate response model structure | All fields present, correct types | **PASSED** |

## 3.3 Discovery Service (LLM) Tests

**Test File:** _test_discovery_llm.py_

| **Test Name** | **Description** | **Expected** | **Status** |
| --- | --- | --- | --- |
| **Ollama Connection** | Verify Ollama is running | Connection successful | **PASSED** |
| **llama3.2 Model** | Model is loaded and ready | Model available | **PASSED** |
| **Discovery Health** | Discovery endpoint operational | HTTP 200 | **\[PASSED** |
| **Service Selection** | LLM picks correct service for queries | Appropriate service selected | **PASSED** |
| **Various Queries** | Test weather, news, GitHub, arXiv queries | Correct service for each | **PASSED** |

# 4\. Performance and Reliability

## 4.1 Safety Tests

Safety tests validate that the system properly handles malformed requests, enforces input validation, and provides clear error messages without exposing sensitive information.

| **Test Name** | **Description** | **Expected** | **Status** |
| --- | --- | --- | --- |
| **Invalid Query Format** | Send malformed JSON to /query | HTTP 422, validation error | **PASSED** |
| **Missing Required Fields** | Omit required parameters | Clear error message | **PASSED** |
| **Empty Query String** | Send empty user query | Handled gracefully | **PASSED** |

## 4.2 Reliability Tests

Reliability tests confirm stable operation under varied conditions, including consecutive queries, external service failures, and database connectivity issues.

| **Test Name** | **Description** | **Expected** | **Status** |
| --- | --- | --- | --- |
| **Consecutive Sessions** | Multiple queries in sequence | Consistent responses | **PASSED** |
| **Service Timeout** | External API slow/unresponsive | Timeout error handled | **PASSED** |
| **MongoDB Reconnection** | DB connection recovery | Auto-reconnect on failure | **PASSED** |

## 4.3 Performance Metrics

**Database Query Optimization:** N+1 query problem was identified and resolved, reducing service retrieval time from 32 seconds to 2.2 seconds.

**End-to-End Response Time:** \[INSERT MEASURED TIME\] seconds for complete query workflow.

**Template vs LLM Formatting:** Template-based formatting achieves 100% consistency compared to ~60% with LLM formatting (40% failure rate observed during development).

# 5\. Test Environment

**Backend API:** FastAPI running on port 8000

**Chatbot Service:** FastAPI running on port 8001

**Database:** MongoDB (Docker container)

**LLM:** Ollama with llama3.2 model (local)

**Test Framework:** Python asyncio with httpx for HTTP testing

# 6\. Running the Tests

To reproduce these results, ensure all prerequisites are running and execute the test runner:

python run_all_tests.py

For quick validation of core functionality only:

python run_all_tests.py --quick

# 7\. Conclusion

The DVerse UIM prototype demonstrates successful implementation of a Level 2 UIM system, providing intelligent service discovery and metadata-driven invocation capabilities. The test results validate that the system meets the requirements for catalogue functionality, agent interactions, and service invocation while maintaining acceptable performance and reliability characteristics.

Key achievements validated by testing include the Generic Service Invoker's ability to call any registered service using only metadata, the LLM-based discovery service's accurate service selection, and the template-based formatting system's reliable and consistent output generation.