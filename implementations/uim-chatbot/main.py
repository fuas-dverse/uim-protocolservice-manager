"""
DVerse Chatbot Main

Fast system architecture with template-based formatting.
"""
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from models import ChatbotQuery, ChatbotResponse
from service_invoker import GenericServiceInvoker
from fast_system import run_fast_system

load_dotenv()

service_invoker: GenericServiceInvoker = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    global service_invoker

    # Startup
    logger.info("Starting Chatbot Agent Service...")
    logger.info("Using fast system with template-based formatting")

    service_invoker = GenericServiceInvoker()
    logger.info("Service invoker initialized")
    logger.info("Chatbot Agent started successfully")

    yield

    # Shutdown
    logger.info("Shutting down Chatbot Agent...")
    if service_invoker:
        await service_invoker.close()
    logger.info("Chatbot Agent shutdown complete")


app = FastAPI(
    title="DVerse Chatbot Agent",
    description="Fast system with template-based service formatting",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        "version": "1.0.0",
        "architecture": "Fast System",
        "features": [
            "Discovery service integration",
            "Generic service invocation",
            "Template-based formatting",
            "Error handling"
        ]
    }


@app.post("/chat", response_model=ChatbotResponse)
async def chat_endpoint(query: ChatbotQuery) -> ChatbotResponse:
    """
    HTTP endpoint for chatbot queries.

    Example:
        POST /chat
        {
            "user_id": "user-123",
            "message": "Find papers about neural networks",
            "context": {}
        }
    """
    logger.info(f"Received chat query from {query.user_id}: '{query.message}'")

    try:
        result = await process_chat_query(query)
        return result
    except Exception as e:
        logger.error(f"Error processing chat query: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process query: {str(e)}"
        )


async def process_chat_query(query: ChatbotQuery) -> ChatbotResponse:
    """Core logic for processing chat queries."""
    try:
        logger.info(f"Processing query for user {query.user_id}")

        response_text = await run_fast_system(
            user_query=query.message,
            service_invoker=service_invoker,
            query_context=query.context
        )

        response = ChatbotResponse(
            user_id=query.user_id,
            message=response_text,
            query=query.message,
            services_discovered=[],
            service_invocation=None,
            success=True
        )

        logger.info(f"Successfully processed query for {query.user_id}")
        return response

    except Exception as e:
        logger.error(f"Error in process_chat_query: {e}", exc_info=True)
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
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")