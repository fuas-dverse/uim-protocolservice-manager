import os
from dotenv import load_dotenv
from faststream import FastStream
from faststream.nats import NatsBroker
from loguru import logger
import asyncio

from models import QueryMessage, ResponseMessage, ServiceInfo, IntentInfo
from catalogue_client import CatalogueClient

# Load environment variables
load_dotenv()

# Configuration
NATS_URL = os.getenv("NATS_URL", "nats://localhost:4222")
CATALOGUE_URL = os.getenv("CATALOGUE_URL", "http://localhost:8000")

logger.info(f"Initializing AQS (Simple Mode) with NATS_URL={NATS_URL}, CATALOGUE_URL={CATALOGUE_URL}")

# Initialize NATS broker
broker = NatsBroker(NATS_URL)
app = FastStream(broker)

# Initialize catalogue client (will be set in lifespan)
catalogue_client: CatalogueClient = None


@app.on_startup
async def on_startup():
    """Initialize services on startup"""
    global catalogue_client

    logger.info("🚀 Starting Agent Query Service (Keyword-Based Version)...")

    # Initialize catalogue client
    catalogue_client = CatalogueClient(CATALOGUE_URL)

    # Note: Health check skipped (backend doesn't have /health endpoint)
    logger.info("✅ Catalogue client initialized")

    logger.info("✅ AQS started successfully (Keyword-Based Mode)")
    logger.info("ℹ️  Using keyword extraction and matching (no AI)")


@app.on_shutdown
async def on_shutdown():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down Agent Query Service...")

    if catalogue_client:
        await catalogue_client.close()

    logger.info("✅ AQS shutdown complete")


def extract_keywords(text: str) -> list[str]:
    """
    Extract meaningful keywords from query text.

    Simple implementation: remove common words, keep words > 3 chars
    """
    # Common words to ignore
    stop_words = {
        'find', 'me', 'show', 'get', 'what', 'are', 'the', 'is', 'can',
        'you', 'i', 'a', 'an', 'and', 'or', 'for', 'with', 'that', 'this'
    }

    # Split into words and clean
    words = text.lower().split()
    keywords = [
        word.strip('?,!.')
        for word in words
        if len(word) > 3 and word.lower() not in stop_words
    ]

    return keywords


@broker.subscriber("uim.catalogue.query")
@broker.publisher("uim.catalogue.response")
async def handle_agent_query(msg: QueryMessage) -> ResponseMessage:
    """
    Handle natural language queries from agents using simple keyword matching.

    This version does NOT use AI - it's a simple rule-based approach:
    1. Extract keywords from query
    2. Search services using keywords
    3. Get intents for found services
    4. Return structured response

    Args:
        msg: QueryMessage from the agent

    Returns:
        ResponseMessage with query results
    """
    logger.info(f"📨 Received query from {msg.agent_id}: '{msg.message}'")

    try:
        # Extract keywords from query
        keywords = extract_keywords(msg.message)
        search_query = " ".join(keywords) if keywords else msg.message

        logger.info(f"🔍 Original query: '{msg.message}'")
        logger.info(f"🔍 Extracted keywords: {keywords}")
        logger.info(f"🔍 Search query: '{search_query}'")

        # Search for services
        services = await catalogue_client.search_services(query=search_query, limit=10)

        # Client-side filtering (in case backend search doesn't filter)
        if keywords and services:
            # Filter services that match at least one keyword
            filtered_services = []
            for service in services:
                name = service.get('name', '').lower()
                desc = service.get('description', '').lower()
                # Check if any keyword appears in name or description
                if any(kw.lower() in name or kw.lower() in desc for kw in keywords):
                    filtered_services.append(service)
            services = filtered_services if filtered_services else services[:3]  # Fallback to top 3

        logger.info(f"📦 Found {len(services)} services")

        # Get intents for the first few services (if endpoint exists)
        all_intents = []
        for service in services[:3]:  # Only check first 3 to avoid too many requests
            service_id = service.get('id')
            if service_id:
                intents = await catalogue_client.get_service_intents(service_id)
                all_intents.extend(intents)

        logger.info(f"🎯 Found {len(all_intents)} intents (note: intent endpoint may not be available)")

        # Build natural language response
        if services:
            service_names = [s.get('name', 'Unknown') for s in services[:3]]
            if len(services) <= 3:
                response_text = f"Found {len(services)} service(s): {', '.join(service_names)}."
            else:
                response_text = f"Found {len(services)} services. Top matches: {', '.join(service_names)}."

            if all_intents:
                response_text += f" These services offer {len(all_intents)} capabilities."
        else:
            response_text = f"No services found matching '{msg.message}'. Try different keywords."

        # Convert to Pydantic models
        services_info = [
            ServiceInfo(
                id=s.get('id', ''),
                name=s.get('name', ''),
                description=s.get('description'),
                base_url=s.get('base_url'),
                metadata=s.get('metadata', {})
            )
            for s in services
        ]

        intents_info = [
            IntentInfo(
                id=i.get('id', ''),
                name=i.get('name', ''),
                description=i.get('description'),
                service_id=i.get('service_id', ''),
                parameters=i.get('parameters', {})
            )
            for i in all_intents
        ]

        # Build response message
        response = ResponseMessage(
            agent_id=msg.agent_id,
            query=msg.message,
            response=response_text,
            services_found=services_info,
            intents_found=intents_info,
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
        "mode": "keyword-based",
        "nats_connected": True,
        "note": "Backend health check not available"
    }


if __name__ == "__main__":
    logger.info("Starting AQS in Keyword-Based Mode...")
    asyncio.run(app.run())