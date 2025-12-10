import httpx
from pydantic_ai import Agent, RunContext
from dataclasses import dataclass
from typing import Dict, Any, List
from loguru import logger

# Import the generic service invoker
from service_invoker import GenericServiceInvoker


@dataclass
class AgentDependencies:
    """Dependencies for the agent"""
    service_invoker: GenericServiceInvoker
    query_context: Dict[str, Any]


# ULTRA-MINIMAL SYSTEM PROMPT
chatbot_agent = Agent(
    'ollama:llama3.1',
    deps_type=AgentDependencies,
    system_prompt="""You call 2 tools in order:

1. discover_services(exact user query) - do NOT rephrase
2. invoke_service(service from step 1)

Then format the result.

CRITICAL:
- Use user's EXACT words in discover_services
- Do NOT call discover_services twice
- Do NOT skip invoke_service"""
)


@chatbot_agent.tool
async def discover_services(
    ctx: RunContext[AgentDependencies],
    query: str
) -> List[Dict[str, Any]]:
    """
    Find the most appropriate service using Discovery Service.

    IMPORTANT: This should receive the EXACT user query without modification.

    Args:
        query: User's query exactly as they typed it

    Returns:
        List with the selected service
    """
    logger.info(f"🔍 discover_services called with query: '{query}'")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "http://localhost:8000/discovery/discover",
                json={"user_query": query},
                follow_redirects=True
            )
            response.raise_for_status()

            result = response.json()
            selected_service = result.get("service")
            selected_name = result.get("selected_name")

            if selected_service:
                logger.info(f"✅ Discovery selected: {selected_name}")
                return [selected_service]
            else:
                logger.warning("⚠️  No service found")
                return []

    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        return []


@chatbot_agent.tool
async def invoke_service(
    ctx: RunContext[AgentDependencies],
    service_name: str,
    intent_name: str,
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Call a service to get REAL DATA.

    MUST be called after discover_services.

    Args:
        service_name: Name from discover_services (e.g., "arXiv API")
        intent_name: Intent to call (e.g., "search_papers")
        parameters: Parameters dict (e.g., {"search_query": "all:AI", "max_results": 10})

    Returns:
        Real data from the service
    """
    logger.info(f"🚀 invoke_service called: {service_name}.{intent_name}")
    logger.info(f"   Parameters: {parameters}")

    try:
        # Get service metadata via Discovery
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "http://localhost:8000/discovery/discover",
                json={"user_query": service_name},
                follow_redirects=True
            )
            response.raise_for_status()

            data = response.json()
            service = data.get("service")

            if not service:
                logger.error(f"❌ Service not found: {service_name}")
                return {"success": False, "error": f"Service '{service_name}' not found"}

            # Find the intent
            intents = service.get("intents", [])
            intent_metadata = None

            for intent in intents:
                if intent.get("intent_name") == intent_name:
                    intent_metadata = intent
                    break

            if not intent_metadata:
                logger.error(f"❌ Intent not found: {intent_name}")
                available = [i.get("intent_name") for i in intents]
                return {
                    "success": False,
                    "error": f"Intent '{intent_name}' not found. Available: {available}"
                }

            # Call the service
            invoker = ctx.deps.service_invoker

            service_metadata = {
                "name": service.get("name"),
                "service_url": service.get("service_url"),
                "auth_type": service.get("auth_type", "none"),
                "auth_header_name": service.get("auth_header_name"),
                "auth_query_param": service.get("auth_query_param")
            }

            result = await invoker.invoke(
                service_metadata=service_metadata,
                intent_metadata=intent_metadata,
                parameters=parameters
            )

            logger.info(f"✅ Service invocation successful")
            logger.info(f"🔍 Result keys: {result.keys()}")

            # Log specific data based on common patterns
            if "papers" in result:
                logger.info(f"📄 Found {len(result['papers'])} papers")
            elif "items" in result:
                logger.info(f"📋 Found {len(result['items'])} items")
            elif "results" in result:
                logger.info(f"📊 Found {len(result['results'])} results")

            return result

    except Exception as e:
        logger.error(f"❌ Error invoking service: {e}", exc_info=True)
        return {"success": False, "error": str(e)}