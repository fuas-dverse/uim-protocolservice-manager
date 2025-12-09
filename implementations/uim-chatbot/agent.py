"""
DVerse Chatbot Agent - SIMPLIFIED VERSION

Clearer prompts, better error handling, faster responses.
"""
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


# Initialize the Pydantic AI agent with SIMPLER prompt
chatbot_agent = Agent(
    'ollama:llama3.2',
    deps_type=AgentDependencies,
    system_prompt="""You are a helpful assistant that can discover and use services.

When a user asks for something:
1. Call discover_services to find the right service
2. Call invoke_service with the service you found
3. Give the user a friendly response with the results

Be concise and helpful."""
)


@chatbot_agent.tool
async def discover_services(
    ctx: RunContext[AgentDependencies],
    query: str
) -> List[Dict[str, Any]]:
    """
    Find services in the catalogue.

    Args:
        query: What type of service to find (e.g., "papers", "weather", "news")

    Returns:
        List of services with full metadata
    """
    logger.info(f"🔍 discover_services called: query='{query}'")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://localhost:8000/query/",  # Added trailing slash
                json={
                    "query": query,
                    "use_ai": False
                },
                follow_redirects=True  # Follow redirects if needed
            )
            response.raise_for_status()

            data = response.json()
            services = data.get("services_found", [])

            logger.info(f"✅ Found {len(services)} services")

            # Return services with full metadata
            return services

    except httpx.TimeoutException:
        logger.error("⏱️ Backend API timeout")
        return []
    except httpx.HTTPError as e:
        logger.error(f"❌ HTTP error: {e}")
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
    Call a service to get data.

    Args:
        service_name: Name of service (from discover_services)
        intent_name: What action to perform (e.g., "search_papers", "get_current_weather")
        parameters: Parameters needed (e.g., {"query": "AI", "max_results": 5})

    Returns:
        Service response data
    """
    logger.info(f"🚀 invoke_service called: {service_name}.{intent_name}")
    logger.info(f"   Parameters: {parameters}")

    try:
        # First discover the service to get metadata
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://localhost:8000/query/",  # Added trailing slash
                json={"query": service_name, "use_ai": False},
                follow_redirects=True
            )
            response.raise_for_status()

            data = response.json()
            services = data.get("services_found", [])

            if not services:
                logger.error(f"❌ Service '{service_name}' not found")
                return {"error": f"Service '{service_name}' not found"}

            service = services[0]

            # Find the intent
            intents = service.get("intents", [])
            intent_metadata = None

            for intent in intents:
                if intent.get("intent_name") == intent_name:
                    intent_metadata = intent
                    break

            if not intent_metadata:
                logger.error(f"❌ Intent '{intent_name}' not found")
                return {"error": f"Intent '{intent_name}' not found in service"}

            # Call the generic invoker
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
            return result

    except httpx.TimeoutException:
        logger.error("⏱️ Service invocation timeout")
        return {"error": "Service timeout"}
    except Exception as e:
        logger.error(f"❌ Error invoking service: {e}", exc_info=True)
        return {"error": str(e)}