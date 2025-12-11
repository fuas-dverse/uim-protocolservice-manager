"""
Discovery Controller

REST API endpoint for LLM-based service discovery.
Provides intelligent service selection using natural language queries.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from logicLayer.Logic.discoveryLogic import DiscoveryLogic
from DAL.serviceDAL import ServiceDAL
from Presentation.Viewmodel.discoveryViewmodel import (
    DiscoveryRequest,
    DiscoveryResponse
)

router = APIRouter()


def get_discovery_logic() -> DiscoveryLogic:
    """Dependency injection for discovery logic"""
    service_dal = ServiceDAL()
    return DiscoveryLogic(service_dal)


@router.post(
    "/discover",
    response_model=DiscoveryResponse,
    summary="Discover service using AI",
    description="""
    Use LLM to intelligently select the most appropriate service based on a natural language query.
    
    The service is selected by analyzing intent tags and descriptions across all available services.
    Uses Ollama with llama3.2 model for intelligent selection.
    
    Example queries:
    - "Find papers about needle in a haystack"
    - "What's the weather in Amsterdam?"
    - "Show me trending GitHub repos"
    - "Search for music by The Beatles"
    """
)
async def discover_service(
    request: DiscoveryRequest,
    logic: DiscoveryLogic = Depends(get_discovery_logic)
):
    """
    Discover the best service for a user query.

    The LLM analyzes:
    - Service descriptions
    - Intent tags (aggregated from all intents)
    - Intent names and capabilities

    Returns the complete service object with all intents.
    """
    try:
        service = await logic.discover_service(request.user_query)

        return DiscoveryResponse(
            service=service,
            selected_name=service["name"],
            reasoning=f"Selected based on query: '{request.user_query}'"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Discovery failed: {str(e)}"
        )


@router.get(
    "/health",
    summary="Discovery service health check",
    description="Check if the discovery service and LLM backend are operational"
)
async def health_check():
    """Check if discovery service is operational"""
    return {
        "status": "healthy",
        "service": "discovery",
        "llm_backend": "ollama",
        "llm_model": "llama3.2"
    }