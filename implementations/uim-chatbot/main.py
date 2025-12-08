"""
Chatbot Agent Service

A chatbot that:
1. Discovers services via AQS (Agent Query Service)
2. Invokes discovered services to get real data
3. Provides both HTTP (web) and NATS (messaging) interfaces

Architecture:
    User → HTTP/NATS → Chatbot → AQS → Catalogue
                     ↓
                 Service Invoker → External APIs (arXiv, etc.)
"""
import asyncio
import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from faststream import FastStream
from faststream.nats import NatsBroker
from loguru import logger
from nats.aio.client import Client as NATS

from models import ChatbotQuery, ChatbotResponse, ServiceInvocationResult
from service_invoker import ServiceInvoker
from agent import chatbot_agent, AgentDependencies

# Load environment variables
load_dotenv()

# Configuration
NATS_URL = os.getenv("NATS_URL", "nats://localhost:4222")
AQS_AVAILABLE = os.getenv("AQS_AVAILABLE", "true").lower() == "true"

logger.info(f"Initializing Chatbot Agent with NATS_URL={NATS_URL}")

# Initialize FastAPI
app = FastAPI(
    title="DVerse Chatbot Agent",
    description="A chatbot that discovers and invokes research services",
    version="1.0.0"
)

# Add CORS middleware for web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize NATS broker for messaging
broker = NatsBroker(NATS_URL)
faststream_app = FastStream(broker)

# Global instances
service_invoker: ServiceInvoker = None
nats_client: NATS = None


@app.on_event("startup")
async def startup():
    """Initialize services on startup"""
    global service_invoker, nats_client

    logger.info("🚀 Starting Chatbot Agent Service...")

    # Initialize service invoker
    service_invoker = ServiceInvoker()
    logger.info("✅ Service invoker initialized")

    # Initialize NATS client for AQS communication
    nats_client = NATS()
    try:
        await nats_client.connect(NATS_URL)
        logger.info("✅ Connected to NATS")
    except Exception as e:
        logger.warning(f"⚠️  Could not connect to NATS: {e}")
        logger.warning("   Chatbot will work in limited mode (no AQS integration)")

    logger.info("✅ Chatbot Agent started successfully")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    global service_invoker, nats_client

    logger.info("🛑 Shutting down Chatbot Agent...")

    if service_invoker:
        await service_invoker.close()

    if nats_client and nats_client.is_connected:
        await nats_client.close()

    logger.info("✅ Chatbot Agent shutdown complete")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "DVerse Chatbot Agent",
        "status": "running",
        "nats_connected": nats_client.is_connected if nats_client else False,
        "aqs_available": AQS_AVAILABLE
    }


@app.post("/chat", response_model=ChatbotResponse)
async def chat_endpoint(query: ChatbotQuery) -> ChatbotResponse:
    """
    HTTP endpoint for chatbot queries.

    This is the web interface - users can POST queries here.
    """
    logger.info(f"📨 Received HTTP chat query from {query.user_id}: '{query.message}'")

    try:
        # Process the query
        result = await process_chat_query(query)
        return result

    except Exception as e:
        logger.error(f"Error processing HTTP chat query: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process query: {str(e)}"
        )


async def process_chat_query(query: ChatbotQuery) -> ChatbotResponse:
    """
    Core logic for processing chat queries.

    This is shared between HTTP and NATS interfaces.
    """
    try:
        # Create dependencies for the agent
        deps = AgentDependencies(
            service_invoker=service_invoker,
            user_id=query.user_id,
            query_context=query.context
        )

        # Run the Pydantic AI agent
        logger.info(f"🤖 Running chatbot agent for user {query.user_id}")
        result = await chatbot_agent.run(query.message, deps=deps)

        # With plain text output, result.data is just a string
        response_text = result.data if isinstance(result.data, str) else str(result.data)

        # Build response
        response = ChatbotResponse(
            user_id=query.user_id,
            message=response_text,
            query=query.message,
            services_discovered=["arXiv API"],  # Hardcode for now
            service_invocation=None,  # We don't track this in simple mode
            success=True
        )

        logger.info(f"✅ Successfully processed query for {query.user_id}")
        return response

    except Exception as e:
        logger.error(f"Error in process_chat_query: {e}")

        # Return error response
        return ChatbotResponse(
            user_id=query.user_id,
            message=f"I encountered an error: {str(e)}",
            query=query.message,
            success=False,
            error=str(e)
        )


# NATS Messaging Interface
@broker.subscriber("uim.chatbot.query")
@broker.publisher("uim.chatbot.response")
async def handle_nats_query(msg: ChatbotQuery) -> ChatbotResponse:
    """
    NATS messaging interface for chatbot queries.

    This allows other agents to communicate with the chatbot via NATS.
    """
    logger.info(f"📨 Received NATS query from {msg.agent_id}: '{msg.message}'")

    # Process using the same logic as HTTP
    response = await process_chat_query(msg)

    logger.info(f"📤 Sending NATS response to {msg.user_id}")
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)