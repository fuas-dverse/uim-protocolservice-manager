import httpx
from typing import Dict, Any, Tuple
from loguru import logger

from service_invoker import GenericServiceInvoker


def format_arxiv_papers(result: Dict[str, Any]) -> str:
    """Fast template-based formatting for arXiv papers"""
    if not result.get("success"):
        return f"Error: {result.get('error', 'Unknown error')}"

    papers = result.get("papers", [])
    if not papers:
        return "No papers found."

    response = f"I found {len(papers)} papers:\n\n"

    for i, paper in enumerate(papers, 1):
        title = paper.get("title", "No title")
        authors = paper.get("authors", [])
        summary = paper.get("summary", "No summary available")
        pdf_url = paper.get("pdf_url", "")

        # Format authors (max 3)
        author_str = ", ".join(authors[:3])
        if len(authors) > 3:
            author_str += f" et al."

        # Truncate summary
        summary_short = summary[:200] + "..." if len(summary) > 200 else summary

        response += f"**{i}. {title}**\n"
        response += f"   Authors: {author_str}\n"
        response += f"   {summary_short}\n"
        if pdf_url:
            response += f"   📄 {pdf_url}\n"
        response += "\n"

    return response


def format_generic_results(result: Dict[str, Any], service_name: str) -> str:
    """Generic template-based formatting for any service"""
    if not result.get("success"):
        error = result.get('error', 'Unknown error')

        # Better error messages for common issues
        if '401' in error or 'Unauthorized' in error:
            return f"Oops! Missing API key for {service_name}. This service requires authentication to work. Please contact your administrator to configure the API key."
        elif '403' in error or 'Forbidden' in error:
            return f"Access denied for {service_name}. The API key may be invalid or doesn't have the required permissions."
        elif '429' in error or 'rate limit' in error.lower():
            return f"Rate limit exceeded for {service_name}. Please try again later."
        else:
            return f"Error calling {service_name}: {error}"

    # Try to find list of items
    items = None
    for key in ['papers', 'items', 'results', 'data', 'tracks', 'repositories']:
        if key in result:
            items = result[key]
            break

    if not items:
        # Just return the raw result formatted nicely
        return f"Result from {service_name}:\n{result}"

    response = f"I found {len(items)} results:\n\n"

    for i, item in enumerate(items[:10], 1):  # Max 10 items
        # Extract title/name
        title = item.get("title") or item.get("name") or item.get("id") or f"Item {i}"

        # Extract description/summary
        desc = item.get("summary") or item.get("description") or item.get("snippet") or ""
        desc_short = desc[:150] + "..." if len(desc) > 150 else desc

        # Extract URL
        url = item.get("url") or item.get("pdf_url") or item.get("link") or item.get("web_url") or ""

        response += f"**{i}. {title}**\n"
        if desc_short:
            response += f"   {desc_short}\n"
        if url:
            response += f"   🔗 {url}\n"
        response += "\n"

    return response


async def run_fast_system(
        user_query: str,
        service_invoker: GenericServiceInvoker,
        query_context: Dict[str, Any] = None
) -> Tuple[str, Dict[str, Any]]:
    """
    Fast orchestrator - no LLM for formatting.

    Flow:
    1. Call Discovery Service directly
    2. Call service directly (no agent)
    3. Format with template (instant)

    Returns:
        Tuple of (formatted_response: str, metadata: Dict)
        metadata includes: service_name, intent_name, success, error (if any)
    """

    metadata = {
        "service_name": None,
        "intent_name": None,
        "success": False,
        "error": None
    }

    try:
        # ===== STEP 1: DISCOVERY =====
        logger.info("=" * 70)
        logger.info("🔍 Calling Discovery Service")
        logger.info("=" * 70)
        logger.info(f"   Query: {user_query}")

        async with httpx.AsyncClient(timeout=60.0) as client:
            discovery_response = await client.post(
                "http://localhost:8000/discovery/discover",
                json={"user_query": user_query},
                follow_redirects=True
            )
            discovery_response.raise_for_status()

            discovery_data = discovery_response.json()
            service = discovery_data.get("service")
            service_name = discovery_data.get("selected_name")

            metadata["service_name"] = service_name

            logger.info(f"✅ Discovery selected: {service_name}")

        # ===== STEP 2: INVOKE SERVICE DIRECTLY =====
        logger.info("=" * 70)
        logger.info("🚀 Invoking service directly")
        logger.info("=" * 70)

        # Get first intent
        intents = service.get("intents", [])
        if not intents:
            error_msg = f"Error: Service '{service_name}' has no intents available"
            metadata["error"] = error_msg
            return error_msg, metadata

        intent = intents[0]
        intent_name = intent.get("intent_name")

        metadata["intent_name"] = intent_name

        logger.info(f"   Service: {service_name}")
        logger.info(f"   Intent: {intent_name}")

        # Build parameters based on service
        # For arXiv, extract search terms from query
        if "arxiv" in service_name.lower():
            # Simple extraction: use query as-is with "all:" prefix
            search_query = f"all:{user_query.replace('Find papers about ', '').replace('Search for ', '')}"
            parameters = {
                "search_query": search_query,
                "max_results": 10,
                "sortBy": "relevance",
                "sortOrder": "descending"
            }
        else:
            # Generic: use query as main parameter
            parameters = {"query": user_query, "limit": 10}

        logger.info(f"   Parameters: {parameters}")

        # Call service
        service_metadata = {
            "name": service.get("name"),
            "service_url": service.get("service_url"),
            "auth_type": service.get("auth_type", "none"),
            "auth_header_name": service.get("auth_header_name"),
            "auth_query_param": service.get("auth_query_param")
        }

        intent_metadata = {
            "intent_name": intent.get("intent_name"),
            "http_method": intent.get("http_method", "POST"),
            "endpoint_path": intent.get("endpoint_path", ""),
            "input_parameters": intent.get("input_parameters", [])
        }

        try:
            result = await service_invoker.invoke(
                service_metadata=service_metadata,
                intent_metadata=intent_metadata,
                parameters=parameters
            )

            logger.info(f"✅ Service invoked successfully")
            logger.info(f"   Result keys: {result.keys()}")

            # Check for authentication errors even in "successful" results
            if not result.get("success"):
                error = result.get("error", "Unknown error")
                if "401" in error or "authentication" in error.lower() or "api key" in error.lower():
                    metadata["error"] = f"Authentication error: Missing or invalid API key for {service_name}"
                    formatted_response = f"Oops! Missing API key for {service_name}. This service requires authentication. Please contact your administrator to configure the API key."
                    return formatted_response, metadata
                else:
                    metadata["error"] = error
                    formatted_response = format_generic_results(result, service_name)
                    return formatted_response, metadata

            # ===== STEP 3: FORMAT RESPONSE =====
            logger.info("=" * 70)
            logger.info("📝 Formatting response")
            logger.info("=" * 70)

            if "arxiv" in service_name.lower():
                formatted_response = format_arxiv_papers(result)
            else:
                formatted_response = format_generic_results(result, service_name)

            metadata["success"] = True
            logger.info(f"✅ Response formatted successfully")

            return formatted_response, metadata

        except Exception as invoke_error:
            logger.error(f"❌ Error invoking service: {invoke_error}")

            # Check if it's an authentication error
            error_str = str(invoke_error)
            if "401" in error_str or "authentication" in error_str.lower() or "unauthorized" in error_str.lower():
                metadata["error"] = f"Authentication error: {error_str}"
                formatted_response = f"Oops! Missing API key for {service_name}. This service requires authentication. Please contact your administrator to configure the API key."
            else:
                metadata["error"] = error_str
                formatted_response = f"Error calling {service_name}: {error_str}"

            return formatted_response, metadata

    except httpx.HTTPStatusError as e:
        logger.error(f"❌ HTTP error during discovery: {e}")

        if e.response.status_code == 401:
            error_msg = f"Authentication error: Missing API key for discovery service"
        else:
            error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"

        metadata["error"] = error_msg
        return error_msg, metadata

    except httpx.RequestError as e:
        logger.error(f"❌ Network error: {e}")
        error_msg = f"Could not connect to discovery service at http://localhost:8000. Is it running?"
        metadata["error"] = error_msg
        return error_msg, metadata

    except Exception as e:
        logger.error(f"❌ Unexpected error in fast_system: {e}", exc_info=True)
        error_msg = f"Unexpected error: {str(e)}"
        metadata["error"] = error_msg
        return error_msg, metadata