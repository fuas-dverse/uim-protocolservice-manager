from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from models import ChatbotQuery, ChatbotResponse
from service_invoker import GenericServiceInvoker
from agent import chatbot_agent, AgentDependencies

# Load environment variables
load_dotenv()

# Global service invoker instance
service_invoker: GenericServiceInvoker = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events.
    Replaces deprecated @app.on_event decorators.
    """
    global service_invoker

    # Startup
    logger.info("🚀 Starting Chatbot Agent Service...")

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
    title="DVerse Chatbot Agent",
    description="A chatbot that discovers and invokes services dynamically",
    version="2.0.0",
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


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "DVerse Chatbot Agent",
        "status": "running",
        "version": "2.0.0",
        "features": [
            "Generic service invocation",
            "Dynamic service discovery",
            "Multi-service support (arXiv, OpenWeather, News, etc.)"
        ]
    }


@app.post("/chat", response_model=ChatbotResponse)
async def chat_endpoint(query: ChatbotQuery) -> ChatbotResponse:
    """
    HTTP endpoint for chatbot queries.

    This is the main web interface - users can POST queries here.

    Example:
        POST /chat
        {
            "user_id": "test_user",
            "message": "Find papers about neural networks",
            "context": {}
        }
    """
    logger.info(f"📨 Received HTTP chat query from {query.user_id}: '{query.message}'")

    try:
        # Process the query
        result = await process_chat_query(query)
        return result

    except Exception as e:
        logger.error(f"❌ Error processing HTTP chat query: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process query: {str(e)}"
        )


async def process_chat_query(query: ChatbotQuery) -> ChatbotResponse:
    """
    Core logic for processing chat queries.

    Uses Pydantic AI agent to:
    1. Understand user intent
    2. Discover appropriate services from catalogue
    3. Invoke services to get real data
    4. Format and return results
    """
    try:
        # Create dependencies for the agent
        deps = AgentDependencies(
            service_invoker=service_invoker,
            query_context=query.context
        )

        # Run the Pydantic AI agent
        logger.info(f"🤖 Running chatbot agent for user {query.user_id}")
        result = await chatbot_agent.run(query.message, deps=deps)

        # Extract response text
        response_text = result.data if isinstance(result.data, str) else str(result.data)

        # Build response
        response = ChatbotResponse(
            user_id=query.user_id,
            message=response_text,
            query=query.message,
            services_discovered=[],  # Could extract from agent if needed
            service_invocation=None,
            success=True
        )

        logger.info(f"✅ Successfully processed query for {query.user_id}")
        return response

    except Exception as e:
        logger.error(f"❌ Error in process_chat_query: {e}", exc_info=True)

        # Return error response
        return ChatbotResponse(
            user_id=query.user_id,
            message=f"I encountered an error: {str(e)}",
            query=query.message,
            success=False,
            error=str(e)
        )


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting chatbot server on http://localhost:8001")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )