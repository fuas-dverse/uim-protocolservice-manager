"""
Pydantic AI agent for the chatbot - SIMPLIFIED VERSION

This agent:
1. Receives natural language queries from users
2. Discovers relevant services via HTTP API
3. Invokes discovered services via ServiceInvoker
4. Returns plain text results (NO structured output validation)
"""
from pydantic_ai import Agent, RunContext
from typing import Dict, Any
from dataclasses import dataclass
from loguru import logger
import httpx

from service_invoker import ServiceInvoker


@dataclass
class AgentDependencies:
    """
    Dependencies injected into the agent at runtime.
    """
    service_invoker: ServiceInvoker
    user_id: str
    query_context: Dict[str, Any]


# Initialize the Pydantic AI agent with Ollama
# Using simple string format compatible with pydantic-ai 0.0.14
chatbot_agent = Agent(
    'ollama:qwen2.5',  # Simple string format - works in all versions
    deps_type=AgentDependencies,
    # NO result_type - just plain text!
    system_prompt="""You are a helpful research assistant chatbot.

IMPORTANT: When users ask for research papers on ANY topic:
1. Use discover_services with query "research papers" or "papers" to find arXiv
2. Then use invoke_service with the user's TOPIC (e.g., "multi-agent systems") as the search query

Example:
User: "Find recent papers about multi-agent systems"
Step 1: discover_services(query="research papers") → finds arXiv
Step 2: invoke_service(service_name="arXiv API", intent_name="search_papers", parameters={"query": "multi-agent systems"})

The discover_services tool finds WHAT SERVICE to use (arXiv for papers).
The invoke_service tool searches arXiv FOR the topic the user wants.

Always search for the SERVICE TYPE first, not the topic!
"""
)


@chatbot_agent.tool
async def discover_services(
    ctx: RunContext[AgentDependencies],
    query: str
) -> Dict[str, Any]:
    """
    Query the Backend API to discover services in the catalogue.

    Args:
        query: Natural language query (e.g., "research papers", "academic articles")

    Returns:
        Services and intents found in the catalogue
    """
    logger.info(f"Agent tool called: discover_services(query='{query}')")

    try:
        # Call merged Backend API at /query endpoint (HTTP, not NATS)
        api_url = "http://localhost:8000/query/"

        payload = {
            "query": query,
            "agent_id": f"chatbot-{ctx.deps.user_id}",
            "context": ctx.deps.query_context,
            "use_ai": False  # Use keyword mode
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, json=payload, timeout=10.0)
            response.raise_for_status()
            data = response.json()

        logger.info(f"API returned {len(data.get('services_found', []))} services")

        return {
            "services": data.get("services_found", []),
            "intents": data.get("intents_found", []),
            "api_response": data.get("response", "")
        }

    except Exception as e:
        logger.error(f"Error discovering services via API: {e}")
        return {
            "services": [],
            "intents": [],
            "error": str(e)
        }


@chatbot_agent.tool
async def invoke_service(
    ctx: RunContext[AgentDependencies],
    service_name: str,
    service_url: str,
    intent_name: str,
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Invoke an external service to get real data.

    Args:
        service_name: Name of the service (e.g., "arXiv API")
        service_url: Base URL of the service
        intent_name: Intent to invoke (e.g., "search_papers")
        parameters: Parameters for the intent (e.g., {"query": "multi-agent", "max_results": 5})

    Returns:
        Data returned from the service
    """
    logger.info(f"Agent tool called: invoke_service({service_name}, {intent_name})")

    try:
        invoker = ctx.deps.service_invoker

        result = await invoker.invoke(
            service_name=service_name,
            service_url=service_url,
            intent_name=intent_name,
            parameters=parameters
        )

        logger.info(f"Service invocation successful")

        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        logger.error(f"Error invoking service: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@chatbot_agent.system_prompt
async def add_contextual_instructions(ctx: RunContext[AgentDependencies]) -> str:
    """
    Add dynamic instructions based on the user's context.
    """
    user_id = ctx.deps.user_id
    context = ctx.deps.query_context

    instructions = f"\nYou are currently helping user: {user_id}\n"

    if context.get("previous_queries"):
        prev = context["previous_queries"]
        instructions += f"\nUser's recent queries: {prev}\n"

    if context.get("preferred_services"):
        prefs = context["preferred_services"]
        instructions += f"\nUser prefers these services: {', '.join(prefs)}\n"

    return instructions