"""
DVerse Chatbot Main - SPLIT ENDPOINT SYSTEM

Splits chat into two endpoints for better UX:
1. /chat/discover - Returns which service will be used
2. /chat/invoke - Invokes the service and returns results

This allows frontend to show "Using X service..." before results arrive.
"""
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from models import ChatbotQuery, ChatbotResponse, ServiceInvocationResult
from service_invoker import GenericServiceInvoker
import httpx

# Load environment variables
load_dotenv()

# Global service invoker instance
service_invoker: GenericServiceInvoker = None


# ==================== NEW MODELS ====================

class DiscoverRequest(BaseModel):
    """Request for service discovery"""
    user_id: str
    message: str


class DiscoverResponse(BaseModel):
    """Response from discovery - just the service info"""
    user_id: str
    query: str
    service_name: str
    intent_name: str
    service_data: Dict[str, Any]  # Full service metadata for invoke step


class InvokeRequest(BaseModel):
    """Request for service invocation"""
    user_id: str
    query: str
    service_name: str
    intent_name: str
    service_data: Dict[str, Any]
    parameters: Optional[Dict[str, Any]] = None


# ==================== LIFESPAN ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events.
    """
    global service_invoker

    # Startup
    logger.info("🚀 Starting Chatbot Agent Service...")
    logger.info("   Using SPLIT ENDPOINT SYSTEM")

    # Initialize service invoker
    service_invoker = GenericServiceInvoker()
    logger.info("✅ Service invoker initialized")

    logger.info("✅ Chatbot Agent started successfully")

    yield  # Application runs here

    # Shutdown
    logger.info("🛑 Shutting down Chatbot Agent...")

    if service_invoker:
        await service_invoker.close()

    logger.info("✅ Chatbot Agent shutdown complete")


# Initialize FastAPI with lifespan
app = FastAPI(
    title="DVerse Chatbot Agent - Split Endpoint System",
    description="Discover and invoke services in separate steps for better UX",
    version="3.2.0",
    lifespan=lifespan
)

# Add CORS middleware for web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== ENDPOINTS ====================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "DVerse Chatbot Agent",
        "status": "running",
        "version": "3.2.0",
        "architecture": "Split Endpoint System",
        "features": [
            "NEW: Separate discover and invoke endpoints",
            "Better UX - show service before results",
            "Forced structured outputs with Pydantic",
            "Service invocation metadata"
        ]
    }


@app.post("/chat/discover", response_model=DiscoverResponse)
async def discover_endpoint(request: DiscoverRequest) -> DiscoverResponse:
    """
    STEP 1: Discover which service to use

    This is fast (~2-3 seconds) and returns just the service selection.
    Frontend can show "Using X service..." immediately.
    """
    logger.info(f"🔍 [DISCOVER] Query from {request.user_id}: '{request.message}'")

    try:
        # Call Discovery Service
        async with httpx.AsyncClient(timeout=60.0) as client:
            discovery_response = await client.post(
                "http://localhost:8000/discovery/discover",
                json={"user_query": request.message},
                follow_redirects=True
            )
            discovery_response.raise_for_status()

            discovery_data = discovery_response.json()
            service = discovery_data.get("service")
            service_name = discovery_data.get("selected_name")

            # Get first intent
            intents = service.get("intents", [])
            if not intents:
                raise HTTPException(
                    status_code=404,
                    detail=f"Service '{service_name}' has no intents available"
                )

            intent = intents[0]
            intent_name = intent.get("intent_name")

            logger.info(f"✅ [DISCOVER] Selected: {service_name} / {intent_name}")

            return DiscoverResponse(
                user_id=request.user_id,
                query=request.message,
                service_name=service_name,
                intent_name=intent_name,
                service_data=service  # Pass full service for invoke step
            )

    except httpx.HTTPStatusError as e:
        logger.error(f"❌ [DISCOVER] HTTP error: {e}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Discovery service error: {e.response.text}"
        )
    except httpx.RequestError as e:
        logger.error(f"❌ [DISCOVER] Network error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Could not connect to discovery service. Is it running on port 8000?"
        )
    except Exception as e:
        logger.error(f"❌ [DISCOVER] Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/invoke", response_model=ChatbotResponse)
async def invoke_endpoint(request: InvokeRequest) -> ChatbotResponse:
    """
    STEP 2: Invoke the service and get results

    This takes longer (~10-15 seconds) as it calls the external API.
    """
    logger.info(f"🚀 [INVOKE] Calling {request.service_name} / {request.intent_name}")

    try:
        service = request.service_data
        intent = None

        # Find the intent
        for i in service.get("intents", []):
            if i.get("intent_name") == request.intent_name:
                intent = i
                break

        if not intent:
            raise HTTPException(
                status_code=404,
                detail=f"Intent '{request.intent_name}' not found in service"
            )

        # Build parameters based on service
        if "arxiv" in request.service_name.lower():
            # Extract search terms from query
            search_query = f"all:{request.query.replace('Find papers about ', '').replace('Search for ', '')}"
            parameters = {
                "search_query": search_query,
                "max_results": 10,
                "sortBy": "relevance",
                "sortOrder": "descending"
            }
        else:
            # Generic parameters
            parameters = request.parameters or {"query": request.query, "limit": 10}

        logger.info(f"   [INVOKE] Parameters: {parameters}")

        # Build metadata
        service_metadata = {
            "name": service.get("name"),
            "service_url": service.get("service_url"),
            "auth_type": service.get("auth_type", "none"),
            "auth_header_name": service.get("auth_header_name"),
            "auth_query_param": service.get("auth_query_param")
        }

        intent_metadata = {
            "intent_name": intent.get("intent_name"),
            "http_method": intent.get("http_method", "POST"),
            "endpoint_path": intent.get("endpoint_path", ""),
            "input_parameters": intent.get("input_parameters", [])
        }

        # Invoke the service
        try:
            result = await service_invoker.invoke(
                service_metadata=service_metadata,
                intent_metadata=intent_metadata,
                parameters=parameters
            )

            logger.info(f"✅ [INVOKE] Service call successful")

            # Check for errors in result
            if not result.get("success"):
                error = result.get("error", "Unknown error")

                # Format user-friendly error messages
                if "401" in error or "authentication" in error.lower():
                    error_msg = f"Oops! Missing API key for {request.service_name}. This service requires authentication. Please contact your administrator to configure the API key."
                elif "403" in error:
                    error_msg = f"Access denied for {request.service_name}. The API key may be invalid."
                elif "429" in error:
                    error_msg = f"Rate limit exceeded for {request.service_name}. Please try again later."
                else:
                    error_msg = f"Error calling {request.service_name}: {error}"

                return ChatbotResponse(
                    user_id=request.user_id,
                    message=error_msg,
                    query=request.query,
                    services_discovered=[request.service_name],
                    service_invocation=ServiceInvocationResult(
                        service_name=request.service_name,
                        intent_name=request.intent_name,
                        success=False,
                        error=error
                    ),
                    success=False,
                    error=error
                )

            # Check if this is arXiv with papers
            if "arxiv" in request.service_name.lower() and result.get("papers"):
                papers_data = result.get("papers", [])

                return ChatbotResponse(
                    user_id=request.user_id,
                    message=f"Found {len(papers_data)} papers:",  # Simple message
                    query=request.query,
                    services_discovered=[request.service_name],
                    service_invocation=ServiceInvocationResult(
                        service_name=request.service_name,
                        intent_name=request.intent_name,
                        success=True,
                        data={"papers": papers_data}  # Structured data for frontend
                    ),
                    success=True
                )
            else:
                # Other services - use text formatting
                formatted_response = format_result(result, request.service_name)

                return ChatbotResponse(
                    user_id=request.user_id,
                    message=formatted_response,
                    query=request.query,
                    services_discovered=[request.service_name],
                    service_invocation=ServiceInvocationResult(
                        service_name=request.service_name,
                        intent_name=request.intent_name,
                        success=True,
                        data=None
                    ),
                    success=True
                )

        except Exception as invoke_error:
            logger.error(f"❌ [INVOKE] Error: {invoke_error}")

            error_str = str(invoke_error)
            if "401" in error_str or "authentication" in error_str.lower():
                error_msg = f"Oops! Missing API key for {request.service_name}. This service requires authentication."
            else:
                error_msg = f"Error calling {request.service_name}: {error_str}"

            return ChatbotResponse(
                user_id=request.user_id,
                message=error_msg,
                query=request.query,
                services_discovered=[request.service_name],
                service_invocation=ServiceInvocationResult(
                    service_name=request.service_name,
                    intent_name=request.intent_name,
                    success=False,
                    error=error_str
                ),
                success=False,
                error=error_str
            )

    except Exception as e:
        logger.error(f"❌ [INVOKE] Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ==================== HELPER FUNCTIONS ====================

def format_result(result: Dict[str, Any], service_name: str) -> str:
    """Format service results for display"""

    # Handle arXiv papers - return minimal text since frontend renders them
    if "papers" in result:
        papers = result.get("papers", [])
        if not papers:
            return "No papers found."

        # Just return count, frontend will render the structured data
        return f"Found {len(papers)} papers:"

    # Generic formatting for other services
    items = None
    for key in ['items', 'results', 'data', 'tracks', 'repositories']:
        if key in result:
            items = result[key]
            break

    if not items:
        return f"Result from {service_name}:\n{result}"

    response = f"I found {len(items)} results:\n\n"

    for i, item in enumerate(items[:10], 1):
        title = item.get("title") or item.get("name") or f"Item {i}"
        desc = item.get("summary") or item.get("description") or ""
        url = item.get("url") or item.get("link") or ""

        desc_short = desc[:150] + "..." if len(desc) > 150 else desc

        response += f"**{i}. {title}**\n"
        if desc_short:
            response += f"   {desc_short}\n"
        if url:
            response += f"   🔗 {url}\n"
        response += "\n"

    return response


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting chatbot server on http://localhost:8001")
    logger.info("Using SPLIT ENDPOINT SYSTEM")
    logger.info("Version 3.2.0 - Discover and invoke in separate steps")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )