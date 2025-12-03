"""
Pydantic AI agent for conversational catalogue queries.

This agent uses Pydantic AI to interpret natural language queries from agents
and translate them into structured catalogue API calls.
"""
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel
from typing import List, Dict, Any
from dataclasses import dataclass
from loguru import logger

from catalogue_client import CatalogueClient
from models import ServiceInfo, IntentInfo


@dataclass
class AgentDependencies:
    """
    Dependencies injected into the agent at runtime.
    
    This allows us to pass the catalogue client and other context
    to the agent's tools and instructions.
    """
    catalogue_client: CatalogueClient
    agent_id: str
    query_context: Dict[str, Any]


class CatalogueQueryResult(BaseModel):
    """Structured output from the agent"""
    summary: str
    services: List[ServiceInfo]
    intents: List[IntentInfo]
    recommendations: List[str] = []


# Initialize the Pydantic AI agent
catalogue_agent = Agent(
    'openai:gpt-4o-mini',  # Using mini for cost efficiency
    deps_type=AgentDependencies,
    result_type=CatalogueQueryResult,
    system_prompt="""You are an intelligent assistant helping AI agents discover and interact with services in the UIM (Unified Intent Mediator) catalogue.

Your role is to:
1. Understand natural language queries from agents
2. Search the catalogue for relevant services and intents
3. Provide clear, structured responses with actionable recommendations

When an agent asks about services:
- Use the search_services tool to find matching services
- Use the get_service_intents tool to discover what each service can do
- Recommend the most relevant intents based on the agent's needs

Be concise but informative. Focus on helping agents discover the right service and intent combinations.

Example queries you might receive:
- "Find me weather services"
- "What services can send emails?"
- "I need to store data, what's available?"
- "Show me all payment processing intents"
"""
)


@catalogue_agent.tool
async def search_services(
    ctx: RunContext[AgentDependencies],
    query: str,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Search for services in the catalogue by name or description.
    
    Args:
        query: Search query (e.g., "weather", "email", "payment")
        limit: Maximum number of results to return (default: 5)
    
    Returns:
        List of matching services with their details
    """
    logger.info(f"Agent tool called: search_services(query='{query}', limit={limit})")
    
    client = ctx.deps.catalogue_client
    services = await client.search_services(query=query, limit=limit)
    
    return services


@catalogue_agent.tool
async def get_service_intents(
    ctx: RunContext[AgentDependencies],
    service_id: str
) -> List[Dict[str, Any]]:
    """
    Get all intents (capabilities) for a specific service.
    
    Args:
        service_id: The ID of the service to get intents for
    
    Returns:
        List of intents with their parameters and descriptions
    """
    logger.info(f"Agent tool called: get_service_intents(service_id='{service_id}')")
    
    client = ctx.deps.catalogue_client
    intents = await client.get_service_intents(service_id)
    
    return intents


@catalogue_agent.tool
async def search_intents(
    ctx: RunContext[AgentDependencies],
    query: str,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Search for intents across all services by name or description.
    
    Args:
        query: Search query (e.g., "forecast", "send", "store")
        limit: Maximum number of results to return (default: 5)
    
    Returns:
        List of matching intents with their service information
    """
    logger.info(f"Agent tool called: search_intents(query='{query}', limit={limit})")
    
    client = ctx.deps.catalogue_client
    intents = await client.search_intents(query=query, limit=limit)
    
    return intents


@catalogue_agent.tool
async def get_service_details(
    ctx: RunContext[AgentDependencies],
    service_id: str
) -> Dict[str, Any]:
    """
    Get detailed information about a specific service.
    
    Args:
        service_id: The ID of the service
    
    Returns:
        Detailed service information including metadata
    """
    logger.info(f"Agent tool called: get_service_details(service_id='{service_id}')")
    
    client = ctx.deps.catalogue_client
    service = await client.get_service_by_id(service_id)
    
    return service or {}


# Dynamic instructions based on context
@catalogue_agent.system_prompt
async def add_contextual_instructions(ctx: RunContext[AgentDependencies]) -> str:
    """
    Add dynamic instructions based on the agent's context.
    
    This allows us to customize the agent's behavior based on who's asking
    and what they've asked before.
    """
    agent_id = ctx.deps.agent_id
    context = ctx.deps.query_context
    
    instructions = f"\nYou are currently helping agent: {agent_id}\n"
    
    if context.get("previous_services"):
        prev_services = context["previous_services"]
        instructions += f"\nThis agent has previously used: {', '.join(prev_services)}\n"
    
    if context.get("location"):
        location = context["location"]
        instructions += f"\nAgent's context indicates location: {location}\n"
    
    return instructions
