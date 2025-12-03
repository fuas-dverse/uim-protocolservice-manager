import asyncio
import os
from dotenv import load_dotenv
from faststream import FastStream
from faststream.nats import NatsBroker
from loguru import logger

from models import QueryMessage, ResponseMessage, ServiceInfo, IntentInfo
from catalogue_client import CatalogueClient
from agent import catalogue_agent, AgentDependencies

# Load environment variables
load_dotenv()

# Configuration
NATS_URL = os.getenv("NATS_URL", "nats://localhost:4222")
CATALOGUE_URL = os.getenv("CATALOGUE_URL", "http://localhost:8000")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Validate configuration
if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY not set - agent queries will fail")

logger.info(f"Initializing AQS with NATS_URL={NATS_URL}, CATALOGUE_URL={CATALOGUE_URL}")

# Initialize NATS broker
broker = NatsBroker(NATS_URL)
app = FastStream(broker)

# Initialize catalogue client (will be set in lifespan)
catalogue_client: CatalogueClient = None


@app.on_startup
async def on_startup():
    """Initialize services on startup"""
    global catalogue_client
    
    logger.info("🚀 Starting Agent Query Service (AI-Powered Version)...")
    
    # Initialize catalogue client
    catalogue_client = CatalogueClient(CATALOGUE_URL)
    
    # Note: Health check skipped (backend doesn't have /health endpoint)
    logger.info("✅ Catalogue client initialized")

    logger.info("✅ AQS started successfully (AI-Powered Mode)")


@app.on_shutdown
async def on_shutdown():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down Agent Query Service...")

    if catalogue_client:
        await catalogue_client.close()

    logger.info("✅ AQS shutdown complete")


@broker.subscriber("uim.catalogue.query")
@broker.publisher("uim.catalogue.response")
async def handle_agent_query(msg: QueryMessage) -> ResponseMessage:
    """
    Handle natural language queries from agents.

    This is the main entry point for agent queries. It:
    1. Receives a QueryMessage from NATS topic "uim.catalogue.query"
    2. Uses Pydantic AI to interpret the query
    3. Calls catalogue API via tools
    4. Returns a ResponseMessage to NATS topic "uim.catalogue.response"

    Args:
        msg: QueryMessage from the agent

    Returns:
        ResponseMessage with query results
    """
    logger.info(f"📨 Received query from {msg.agent_id}: '{msg.message}'")

    try:
        # Create dependencies for the agent
        deps = AgentDependencies(
            catalogue_client=catalogue_client,
            agent_id=msg.agent_id,
            query_context=msg.context
        )

        # Run the Pydantic AI agent
        logger.info(f"🤖 Running Pydantic AI agent for query: '{msg.message}'")
        result = await catalogue_agent.run(msg.message, deps=deps)

        # Extract structured result
        query_result = result.data

        logger.info(f"✅ Agent found {len(query_result.services)} services, {len(query_result.intents)} intents")

        # Build response message
        response = ResponseMessage(
            agent_id=msg.agent_id,
            query=msg.message,
            response=query_result.summary,
            services_found=query_result.services,
            intents_found=query_result.intents,
            success=True,
            error=None
        )

        logger.info(f"📤 Sending response to {msg.agent_id}")
        return response

    except Exception as e:
        logger.error(f"❌ Error processing query: {e}", exc_info=True)

        # Return error response
        return ResponseMessage(
            agent_id=msg.agent_id,
            query=msg.message,
            response=f"I encountered an error processing your query: {str(e)}",
            services_found=[],
            intents_found=[],
            success=False,
            error=str(e)
        )


# Optional: Health check endpoint via NATS
@broker.subscriber("uim.aqs.health")
@broker.publisher("uim.aqs.health.response")
async def health_check(msg: dict) -> dict:
    """
    Health check endpoint for monitoring.

    Agents or monitoring services can publish to "uim.aqs.health"
    to check if the AQS is running.
    """
    logger.info("Health check requested")

    return {
        "status": "healthy",
        "service": "agent-query-service",
        "mode": "ai-powered",
        "nats_connected": True,
        "note": "Backend health check not available"
    }


if __name__ == "__main__":
    logger.info("Starting AQS via main...")
    asyncio.run(app.run())