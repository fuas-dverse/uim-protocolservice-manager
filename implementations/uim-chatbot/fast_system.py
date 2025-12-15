import httpx
from typing import Dict, Any
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

        author_str = ", ".join(authors[:3])
        if len(authors) > 3:
            author_str += f" et al."

        summary_short = summary[:200] + "..." if len(summary) > 200 else summary

        response += f"**{i}. {title}**\n"
        response += f"   Authors: {author_str}\n"
        response += f"   {summary_short}\n"
        if pdf_url:
            response += f"   {pdf_url}\n"
        response += "\n"

    return response


def format_generic_results(result: Dict[str, Any], service_name: str) -> str:
    """Generic template-based formatting for any service"""
    if not result.get("success"):
        return f"Error: {result.get('error', 'Unknown error')}"

    items = None
    for key in ['papers', 'items', 'results', 'data', 'tracks', 'repositories']:
        if key in result:
            items = result[key]
            break

    if not items:
        return f"Result from {service_name}:\n{result}"

    response = f"I found {len(items)} results:\n\n"

    for i, item in enumerate(items[:10], 1):
        title = item.get("title") or item.get("name") or item.get("id") or f"Item {i}"
        desc = item.get("summary") or item.get("description") or item.get("snippet") or ""
        desc_short = desc[:150] + "..." if len(desc) > 150 else desc
        url = item.get("url") or item.get("pdf_url") or item.get("link") or item.get("web_url") or ""

        response += f"**{i}. {title}**\n"
        if desc_short:
            response += f"   {desc_short}\n"
        if url:
            response += f"   {url}\n"
        response += "\n"

    return response


async def run_fast_system(
    user_query: str,
    service_invoker: GenericServiceInvoker,
    query_context: Dict[str, Any] = None
) -> str:
    """
    Fast orchestrator - no LLM for formatting.

    Flow:
    1. Call Discovery Service directly
    2. Call service directly (no agent)
    3. Format with template (instant)
    """

    try:
        logger.info("=" * 70)
        logger.info("Calling Discovery Service")
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

            logger.info(f"Discovery selected: {service_name}")

        logger.info("=" * 70)
        logger.info("Invoking service")
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

        logger.info(f"Service invocation successful")

        logger.info("=" * 70)
        logger.info("Formatting results")
        logger.info("=" * 70)

        if "arxiv" in service_name.lower():
            formatted = format_arxiv_papers(result)
        else:
            formatted = format_generic_results(result, service_name)

        logger.info(f"Formatted response ready ({len(formatted)} chars)")

        return formatted

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return f"Error: {str(e)}"