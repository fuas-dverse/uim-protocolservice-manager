from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional

from logicLayer.Logic.queryLogic import QueryLogic
from DAL.serviceDAL import ServiceDAL
from DAL.intentDAL import IntentDAL
from Presentation.Viewmodel.queryViewmodel import (
    QueryRequest,
    QueryResponse
)

router = APIRouter()


# Dependency injection for query logic
def get_query_logic() -> QueryLogic:
    """
    Initialize QueryLogic with required DAL dependencies.
    Note: QueryLogic doesn't need its own DAL - it uses existing service/intent DALs.
    """
    service_dal = ServiceDAL()
    intent_dal = IntentDAL()
    logic = QueryLogic(service_dal, intent_dal)
    return logic


@router.post(
    "/",
    response_model=QueryResponse,
    summary="Query the catalogue using natural language",
    description="""
    Query the UIM catalogue using natural language.
    
    This endpoint supports two modes:
    - **Keyword-based**: Fast, simple keyword matching (default)
    - **AI-powered**: Advanced natural language understanding (requires OPENAI_API_KEY)
    
    Examples:
    - "Find me weather services"
    - "Show services that can process payments"
    - "What intents are available for the OpenWeather service?"
    """
)
async def query_catalogue(
    request: QueryRequest,
    logic: QueryLogic = Depends(get_query_logic)
):
    """
    Process a natural language query against the catalogue.
    
    Args:
        request: QueryRequest with the natural language query
        logic: Injected QueryLogic instance
        
    Returns:
        QueryResponse with matching services and intents
        
    Raises:
        HTTPException: If query processing fails
    """
    try:
        # Process the query using QueryLogic
        response = await logic.process_query(
            query=request.query,
            agent_id=request.agent_id,
            context=request.context,
            use_ai=request.use_ai
        )
        
        return response
        
    except ValueError as e:
        # Validation errors (e.g., empty query)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process query: {str(e)}"
        )


@router.get(
    "/health",
    summary="Check query service health",
    description="Check if the query service is operational and which mode (keyword/AI) is available"
)
def query_health(logic: QueryLogic = Depends(get_query_logic)):
    """
    Health check for the query service.
    
    Returns:
        Status information about available query modes
    """
    return {
        "status": "healthy",
        "modes": {
            "keyword": True,
            "ai": logic.is_ai_available()
        }
    }
