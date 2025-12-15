"""
Two-Agent System with Forced Structured Outputs

Agent 1: Discovery Agent - Only finds the right service
Agent 2: Invocation Agent - Only calls the service and formats results

This isolates which part is failing and forces proper responses.
"""
import httpx
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field
from dataclasses import dataclass
from typing import Dict, Any, List
from loguru import logger

from service_invoker import GenericServiceInvoker


@dataclass
class AgentDependencies:
    """Dependencies for agents"""
    service_invoker: GenericServiceInvoker
    query_context: Dict[str, Any]


# ==================== AGENT 1: DISCOVERY ====================

class DiscoveryResult(BaseModel):
    """Forced structured output for Discovery Agent"""
    service_name: str = Field(..., description="Name of the discovered service")
    service_description: str = Field(..., description="What this service does")
    recommended_intent: str = Field(..., description="Which intent to use")
    reasoning: str = Field(..., description="Why this service was selected")


discovery_agent = Agent(
    'ollama:llama3.1',
    deps_type=AgentDependencies,
    result_type=DiscoveryResult,
    system_prompt="""You discover the right service for a user query.

Call discover_services with the user's query, then return:
- service_name: The service you found
- service_description: What it does
- recommended_intent: Which intent to use (e.g., "search_papers")
- reasoning: Why you picked this service

You MUST call discover_services to get this information."""
)


@discovery_agent.tool
async def discover_services(
        ctx: RunContext[AgentDependencies],
        query: str
) -> List[Dict[str, Any]]:
    """
    Find the most appropriate service using Discovery Service.
    """
    logger.info(f"🔍 [AGENT 1] discover_services called: '{query}'")

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
                logger.info(f"✅ [AGENT 1] Discovery selected: {selected_name}")
                return [selected_service]
            else:
                logger.warning("⚠️  [AGENT 1] No service found")
                return []

    except Exception as e:
        logger.error(f"❌ [AGENT 1] Error: {e}", exc_info=True)
        return []


# ==================== AGENT 2: INVOCATION ====================

class InvocationResult(BaseModel):
    """Forced structured output for Invocation Agent"""
    success: bool = Field(..., description="Whether invocation succeeded")
    data_summary: str = Field(..., description="Summary of what was found")
    items_found: int = Field(..., description="Number of items (papers, articles, etc)")
    formatted_response: str = Field(..., description="User-friendly formatted response")


invocation_agent = Agent(
    'ollama:llama3.1',
    deps_type=AgentDependencies,
    result_type=InvocationResult,
    system_prompt="""You invoke a service and format the results.

You MUST call invoke_service with:
- The service name you're given
- The intent name you're given  
- Appropriate parameters

Then return:
- success: true/false
- data_summary: Brief summary
- items_found: Count of items
- formatted_response: Nice formatted text for the user

You MUST call invoke_service to get real data."""
)


@invocation_agent.tool
async def invoke_service(
        ctx: RunContext[AgentDependencies],
        service_name: str,
        intent_name: str,
        parameters: Dict[str, Any]
) -> Dict[str, Any]:

    logger.info(f"🚀 [AGENT 2] invoke_service called: {service_name}.{intent_name}")
    logger.info(f"   [AGENT 2] Parameters: {parameters}")

    try:

        service = ctx.deps.query_context.get('full_service')

        if not service:
            logger.error(f"❌ [AGENT 2] No service in context!")
            return {"success": False, "error": "Service data not provided in context"}

        logger.info(f"✅ [AGENT 2] Using service from context: {service.get('name')}")


        intents = service.get("intents", [])
        intent_metadata = None

        for intent in intents:
            if intent.get("intent_name") == intent_name:
                intent_metadata = intent
                break

        if not intent_metadata:
            logger.error(f"❌ [AGENT 2] Intent not found: {intent_name}")
            available = [i.get("intent_name") for i in intents]
            return {
                "success": False,
                "error": f"Intent '{intent_name}' not found. Available: {available}"
            }


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

        logger.info(f"✅ [AGENT 2] Service invocation successful")
        logger.info(f"🔍 [AGENT 2] Result keys: {result.keys()}")


        if "papers" in result:
            logger.info(f"📄 [AGENT 2] Found {len(result['papers'])} papers")
        elif "items" in result:
            logger.info(f"📋 [AGENT 2] Found {len(result['items'])} items")

        return result

    except Exception as e:
        logger.error(f"❌ [AGENT 2] Error: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


# ==================== ORCHESTRATOR ====================

async def run_two_agent_system(
        user_query: str,
        service_invoker: GenericServiceInvoker,
        query_context: Dict[str, Any] = None
) -> str:
    """
    Simplified orchestrator - skips Agent 1, uses Discovery directly.

    Flow:
    1. Call Discovery Service directly with user's exact query
    2. Agent 2 invokes the service and formats results

    Returns the final formatted response.
    """

    try:
        # ===== STEP 1: CALL DISCOVERY SERVICE DIRECTLY =====
        logger.info("=" * 70)
        logger.info("🔍 Calling Discovery Service directly")
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
            real_service = discovery_data.get("service")
            real_service_name = discovery_data.get("selected_name")

            logger.info(f"✅ Discovery selected: {real_service_name}")


            intents = real_service.get("intents", [])
            if not intents:
                return f"Error: Service '{real_service_name}' has no intents available"

            recommended_intent = intents[0].get("intent_name")
            logger.info(f"   Using intent: {recommended_intent}")


            input_parameters = intents[0].get("input_parameters", [])
            logger.info(f"   Parameters needed: {[p.get('name') for p in input_parameters]}")

        # ===== STEP 2: INVOCATION AGENT =====
        logger.info("=" * 70)
        logger.info("🤖 [AGENT 2] Starting Invocation Agent")
        logger.info("=" * 70)


        deps = AgentDependencies(
            service_invoker=service_invoker,
            query_context={'full_service': real_service}
        )


        param_descriptions = []
        for param in input_parameters:
            param_name = param.get("name")
            param_type = param.get("type", "string")
            param_desc = param.get("description", "")
            required = param.get("required", False)

            param_descriptions.append(
                f"  - {param_name} ({param_type}){' [REQUIRED]' if required else ''}: {param_desc}"
            )

        param_schema_text = "\n".join(param_descriptions) if param_descriptions else "  (No parameters required)"


        invocation_prompt = f"""You must invoke this service:

SERVICE: {real_service_name}
INTENT: {recommended_intent}
USER QUERY: {user_query}

PARAMETERS YOU MUST CREATE:
{param_schema_text}

CRITICAL: Use the EXACT parameter names listed above. Do not rename them.

Example for arXiv API search_papers:
{{
  "search_query": "all:needle haystack LLM",
  "max_results": 10
}}

Now create the parameters and call invoke_service."""

        invocation_result = await invocation_agent.run(invocation_prompt, deps=deps)

        logger.info(f"✅ [AGENT 2] Invocation completed:")
        logger.info(f"   Success: {invocation_result.data.success}")
        logger.info(f"   Items Found: {invocation_result.data.items_found}")
        logger.info(f"   Summary: {invocation_result.data.data_summary}")


        invocation_called_tool = False
        if hasattr(invocation_result, '_all_messages'):
            for msg in invocation_result._all_messages:
                if hasattr(msg, 'parts'):
                    for part in msg.parts:
                        if hasattr(part, 'tool_name') and part.tool_name and 'invoke' in part.tool_name:
                            invocation_called_tool = True
                            break

        if not invocation_called_tool:
            logger.error("❌ [AGENT 2] DID NOT call invoke_service tool!")
            logger.error("   This is the problem - Agent 2 is hallucinating!")
        else:
            logger.info("✅ [AGENT 2] Successfully called invoke_service tool")


        return invocation_result.data.formatted_response

    except AttributeError as e:
        logger.error(f"❌ Orchestrator AttributeError: {e}")
        logger.error(f"   This usually means the agent didn't return the expected structured format")
        logger.error(f"   The agent may have returned an error or unexpected data type")
        return f"Error: Agent returned unexpected format - {str(e)}"
    except KeyError as e:
        logger.error(f"❌ Orchestrator KeyError: {e}")
        logger.error(f"   Missing expected key in agent response")
        return f"Error: Missing data in agent response - {str(e)}"
    except Exception as e:
        logger.error(f"❌ Orchestrator error: {e}", exc_info=True)
        return f"Error: {str(e)}"