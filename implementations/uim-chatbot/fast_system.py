"""
Fast System - Direct service discovery and invocation

Implements a streamlined approach to service discovery and invocation by
calling the Discovery Service directly and using template-based formatting
instead of LLM-based response generation.
"""
import httpx
from typing import Dict, Any
from loguru import logger

from service_invoker import GenericServiceInvoker


def format_arxiv_papers(result: Dict[str, Any]) -> str:
    """Format arXiv papers into readable response"""
    if not result.get("success"):
        return "I couldn't retrieve papers from arXiv. " + result.get("error", "Unknown error")

    papers = result.get("papers", [])
    if not papers:
        return "I didn't find any papers matching your query."

    response = f"I found {len(papers)} papers:\n\n"

    for i, paper in enumerate(papers[:5], 1):
        title = paper.get("title", "Untitled")
        authors = paper.get("authors", "Unknown authors")
        summary = paper.get("summary", "")
        url = paper.get("url", "")

        response += f"**{i}. {title}**\n"
        response += f"   Authors: {authors}\n"
        if summary:
            summary_short = summary[:200] + "..." if len(summary) > 200 else summary
            response += f"   {summary_short}\n"
        if url:
            response += f"   🔗 {url}\n"
        response += "\n"

    return response


def format_generic_results(result: Dict[str, Any], service_name: str) -> str:
    """Format generic service results"""
    if not result.get("success"):
        return f"I couldn't retrieve data from {service_name}. " + result.get("error", "Unknown error")

    items = result.get("items", [])
    if items:
        response = f"I found {len(items)} results from {service_name}:\n\n"
        for i, item in enumerate(items[:5], 1):
            title = item.get("title") or item.get("name", "Item " + str(i))
            desc_short = item.get("description", "")[:100]
            url = item.get("url", "")

            response += f"**{i}. {title}**\n"
            if desc_short:
                response += f"   {desc_short}\n"
            if url:
                response += f"   🔗 {url}\n"
            response += "\n"
        return response

    data = result.get("data", {})
    return f"Results from {service_name}:\n{str(data)[:500]}"


async def run_fast_system(
        user_query: str,
        service_invoker: GenericServiceInvoker,
        query_context: Dict[str, Any] = None
) -> str:
    """
    Execute service discovery and invocation with template-based formatting.

    Process:
    1. Call Discovery Service to find the appropriate service
    2. Extract and format parameters for the selected service
    3. Invoke the service with the formatted parameters
    4. Format results using service-specific templates

    Returns:
        Formatted response string ready for user display
    """
    try:
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

            logger.info(f"✅ Discovery selected: {service_name}")

        logger.info("=" * 70)
        logger.info("🚀 Invoking service")
        logger.info("=" * 70)

        intents = service.get("intents", [])
        if not intents:
            return f"Error: Service '{service_name}' has no intents available"

        intent = intents[0]
        intent_name = intent.get("intent_name")

        logger.info(f"   Service: {service_name}")
        logger.info(f"   Intent: {intent_name}")

        if "arxiv" in service_name.lower():
            search_query = f"all:{user_query.replace('Find papers about ', '').replace('Search for ', '')}"
            parameters = {
                "search_query": search_query,
                "max_results": 10,
                "sortBy": "relevance",
                "sortOrder": "descending"
            }
        else:
            parameters = {"query": user_query, "limit": 10}

        logger.info(f"   Parameters: {parameters}")

        service_metadata = {
            "name": service.get("name"),
            "service_url": service.get("service_url"),
            "auth_type": service.get("auth_type", "none"),
            "auth_header_name": service.get("auth_header_name"),
            "auth_query_param": service.get("auth_query_param")
        }

        result = await service_invoker.invoke(
            service_metadata=service_metadata,
            intent_metadata=intent,
            parameters=parameters
        )

        logger.info(f"✅ Service invocation successful")

        logger.info("=" * 70)
        logger.info("📝 Formatting results")
        logger.info("=" * 70)

        if "arxiv" in service_name.lower():
            formatted = format_arxiv_papers(result)
        else:
            formatted = format_generic_results(result, service_name)

        logger.info(f"✅ Formatted response ready ({len(formatted)} chars)")

        return formatted

    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        return f"Error: {str(e)}"