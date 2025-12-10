"""
DVerse Chatbot Agent - FIXED VERSION

Forces the agent to ALWAYS use tools instead of just explaining.
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


# Initialize the Pydantic AI agent with EXPLICIT tool-use instructions
chatbot_agent = Agent(
    'ollama:llama3.2',
    deps_type=AgentDependencies,
    system_prompt="""You help users by calling tools to get real data, then showing them clean results.

CRITICAL RULES:
1. When you call tools, users CANNOT see the tool calls - only your text response
2. NEVER write tool syntax like {"name": "invoke_service", ...} in your response
3. If discover_services finds 0 services, tell the user you couldn't find a service
4. NEVER make up or invent data - ONLY use data from tool results
5. If you don't have real data, say so - don't hallucinate

Process:
1. Call discover_services
2. If 0 services found → Tell user "I couldn't find a service for that"
3. If service found → Call invoke_service
4. Show formatted results from actual data

BAD Example (hallucination):
discover_services finds 0 services
You respond: "I found 2 tracks: Bohemian Rhapsody..." ❌ WRONG - made up data!

GOOD Example:
discover_services finds 0 services  
You respond: "I couldn't find a music service. Try rephrasing your request." ✅ Honest

WHAT TO DO:
1. User asks question
2. Call tools (discover_services, then invoke_service)
3. Format the results cleanly
4. Show ONLY the formatted results to user

WHAT NOT TO DO:
- Don't show tool syntax
- Don't narrate what you're doing
- Don't show JSON
- Don't explain your process

Just call tools and show results. That's it.

FORMATTING: SIMPLE RULES

1. Check result["success"]
2. Find the main data (usually result["papers"], result["items"], result["data"]["something"])
3. Format as clean list or bullet points
4. Extract URLs ONLY from the actual data - NEVER make up URLs
5. Show URLs directly as text (NOT markdown links - the frontend doesn't render markdown)
6. If a URL field is missing/null/empty, write "(Link not available)" instead

CRITICAL: URL HANDLING
- ONLY use URLs that are actually present in result data
- Check if url/pdf_url/link exists and is not null before showing it
- If url is missing: Show "(PDF not available)" or "(Link not available)"
- NEVER invent URLs
- NEVER write "PDF Link" or "[Link]" without actual URL
- Show URLs as plain text, not markdown

Example with mixed URLs:
Paper 1: {"title": "X", "pdf_url": "https://real.url"} 
→ "**1. X**\n   📄 https://real.url"

Paper 2: {"title": "Y", "pdf_url": null}
→ "**2. Y**\n   📄 (PDF not available)"

Paper 3: {"title": "Z"} (no pdf_url field)
→ "**3. Z**\n   📄 (PDF not available)"

EXAMPLE OF CORRECT EXECUTION:

User: "Find papers about AI"

[Tools execute silently]

Your response:
"I found 3 papers:

**1. Deep Learning Methods**
   Authors: Smith et al.
   📄 https://arxiv.org/pdf/2301.12345

**2. Neural Networks**  
   Authors: Jones
   📄 https://arxiv.org/pdf/2302.54321"

Note: Show URLs as plain text, NOT markdown links.

EXAMPLE:
User: "Find papers about AI"
You MUST:
- Call discover_services(query="papers") 
- Get arXiv service from results
- Call invoke_service(service_name="arXiv API", intent_name="search_papers", parameters={"search_query": "all:AI", "max_results": 5})
- Format response like:
  "I found 5 recent papers on AI:
  
  1. **AI for Computer Vision: A Survey** (2022)
     Authors: Author 1, Author 2
     Summary: This paper provides a comprehensive survey...
     [PDF Link]
  
  2. **Deep Learning for NLP** (2021)
     ..."

You MUST NOT:
- Show raw JSON data to users
- Dump technical parameters or metadata
- Just say "you can search arXiv"
- Give URLs or instructions without using tools
- Offer to "fetch more results" or make follow-up queries
- Call the same tool multiple times for one request

WORKFLOW:
1. User asks → Call discover_services ONCE → Call invoke_service ONCE → Format results nicely → DONE
2. If user wants more, they will ask again in a new message
3. Present ALL the results you got, don't hold back or offer to get more

CRITICAL: Just call tools and format results. No explanations, no JSON dumps, no announcements."""
)


@chatbot_agent.tool
async def discover_services(
    ctx: RunContext[AgentDependencies],
    query: str
) -> List[Dict[str, Any]]:
    """
    Find services in the catalogue that match the query.

    ALWAYS call this first when a user asks for something.

    IMPORTANT: Use simple, single-word keywords. Don't add extra punctuation or context.
    Good: "news", "papers", "weather", "music"
    Bad: "news:technology", "papers about AI", "weather-forecast"

    Args:
        query: Simple keyword for service type (e.g., "papers", "weather", "news", "music")

    Returns:
        List of services with full metadata including intents
    """
    logger.info(f"🔍 discover_services called: query='{query}'")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:  # Increased from 30s to 60s
            response = await client.post(
                "http://localhost:8000/query/",
                json={
                    "query": query,
                    "use_ai": False
                },
                follow_redirects=True
            )
            response.raise_for_status()

            data = response.json()
            services = data.get("services_found", [])

            logger.info(f"✅ Found {len(services)} services")

            # Return services with full metadata
            return services

    except httpx.TimeoutException:
        logger.error("⏱️ Backend API timeout (>60s)")
        logger.error("   This usually means the Backend API is overloaded or MongoDB is slow")
        logger.error("   Try: curl http://localhost:8000/query -X POST -d '{\"query\":\"test\"}'")
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
    Call a service to get REAL DATA.

    ALWAYS call this after discover_services to get actual results.

    Args:
        service_name: Exact name of service from discover_services (e.g., "arXiv API")
        intent_name: Intent to invoke (e.g., "search_papers", "get_current_weather")
        parameters: Parameters for the intent (e.g., {"search_query": "all:AI", "max_results": 5})

    Returns:
        Dict with real data from the service

    Common return formats:
    - Structured: {"success": True, "items": [...], "field": "value"}
    - Nested: {"success": True, "data": {...}}

    IMPORTANT: Dynamically inspect and extract data:
    - Check result["success"] first
    - Look for list fields: items, results, papers, articles, tracks, repositories, etc.
    - Look for URL fields: url, link, href, pdf_url, html_url, web_url, external_url, etc.
    - Extract what's relevant and format cleanly
    - Adapt to whatever structure the service returns
    """
    logger.info(f"🚀 invoke_service called: {service_name}.{intent_name}")
    logger.info(f"   Parameters: {parameters}")

    try:
        # First discover the service to get metadata
        async with httpx.AsyncClient(timeout=60.0) as client:  # Increased timeout
            response = await client.post(
                "http://localhost:8000/query/",
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

            # DEBUG: Log the actual result to see what we got
            logger.info(f"🔍 DEBUG - Result keys: {result.keys()}")
            if "papers" in result:
                logger.info(f"🔍 DEBUG - Number of papers: {len(result['papers'])}")
                if result['papers']:
                    logger.info(f"🔍 DEBUG - First paper: {result['papers'][0]}")

            return result

    except httpx.TimeoutException:
        logger.error("⏱️ Service invocation timeout")
        return {"error": "Service timeout"}
    except Exception as e:
        logger.error(f"❌ Error invoking service: {e}", exc_info=True)
        return {"error": str(e)}