"""
DVerse Chatbot Main - TWO-AGENT SYSTEM

Uses separate Discovery and Invocation agents to isolate the problem.
"""
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from models import ChatbotQuery, ChatbotResponse
from service_invoker import GenericServiceInvoker
from fast_system import run_fast_system

# Load environment variables
load_dotenv()

# Global service invoker instance
service_invoker: GenericServiceInvoker = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events.
    """
    global service_invoker

    # Startup
    logger.info("🚀 Starting Chatbot Agent Service...")
    logger.info("   Using TWO-AGENT SYSTEM with forced structured outputs")

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
    title="DVerse Chatbot Agent - Two-Agent System",
    description="Uses separate Discovery and Invocation agents for better reliability",
    version="3.0.0",
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
        "version": "3.0.0",
        "architecture": "Two-Agent System",
        "features": [
            "Agent 1: Discovery (finds right service)",
            "Agent 2: Invocation (calls service and formats)",
            "Forced structured outputs with Pydantic",
            "Better isolation of failures"
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
        # Process the query with two-agent system
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

    Uses two-agent system:
    1. Agent 1: Discovery - finds the right service
    2. Agent 2: Invocation - calls the service and formats results
    """
    try:
        logger.info(f"🤖 Processing query for user {query.user_id}")
        logger.info("   Using TWO-AGENT SYSTEM")

        # Run the two-agent orchestrator
        response_text = await run_fast_system(
            user_query=query.message,
            service_invoker=service_invoker,
            query_context=query.context
        )

        # Build response
        response = ChatbotResponse(
            user_id=query.user_id,
            message=response_text,
            query=query.message,
            services_discovered=[],  # Could extract from agents if needed
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
    logger.info("Using TWO-AGENT SYSTEM with forced structured outputs")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )