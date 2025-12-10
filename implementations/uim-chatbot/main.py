from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from typing import Dict, Any

from models import ChatbotQuery, ChatbotResponse
from service_invoker import GenericServiceInvoker
from agent import chatbot_agent, AgentDependencies

# Load environment variables
load_dotenv()

# Global service invoker instance
service_invoker: GenericServiceInvoker = None


class HallucinationDetector:
    """Detects when LLM responds without real data"""

    @staticmethod
    def detect_hallucination(response: str, tool_calls_made: list) -> bool:
        """
        Check if response is hallucinated (no invoke_service called)

        Args:
            response: The LLM's text response
            tool_calls_made: List of tool names that were called

        Returns:
            True if hallucination detected
        """
        # Check if invoke_service was called
        invoke_called = any("invoke_service" in str(call) for call in tool_calls_made)

        if not invoke_called:
            logger.warning("⚠️  HALLUCINATION DETECTED: invoke_service was not called")
            return True

        # Check for hallucination indicators in response
        hallucination_indicators = [
            "(PDF not available)" in response and "papers" in response.lower(),
            "(Link not available)" in response,
            "I found" in response and not invoke_called,
            # Common hallucinated paper titles
            "Lost in the Middle" in response,
            "Attention Is All You Need" in response and not invoke_called,
        ]

        if any(hallucination_indicators):
            logger.warning(f"⚠️  HALLUCINATION DETECTED: Response has indicators")
            logger.warning(f"   Response preview: {response[:200]}")
            return True

        return False


async def chat_with_retry(
        user_query: str,
        user_id: str,
        query_context: Dict[str, Any] = None,
        max_retries: int = 2
) -> str:
    """
    Run chatbot with automatic retry on hallucination detection

    Args:
        user_query: User's question
        user_id: User identifier
        query_context: Optional context dict
        max_retries: Maximum number of retries

    Returns:
        Final response text
    """
    deps = AgentDependencies(
        service_invoker=service_invoker,
        query_context=query_context or {}
    )

    detector = HallucinationDetector()

    for attempt in range(max_retries + 1):
        if attempt > 0:
            logger.warning(f"🔄 Retry attempt {attempt}/{max_retries}")
            # Make the prompt more forceful on retry
            query_with_hint = f"""{user_query}

CRITICAL INSTRUCTION: You MUST call invoke_service to get real data. Do NOT respond without calling it. Do NOT make up paper titles, URLs, or any other information."""
        else:
            query_with_hint = user_query

        try:
            # Run the agent
            logger.info(f"🤖 Running chatbot agent (attempt {attempt + 1})")
            result = await chatbot_agent.run(query_with_hint, deps=deps)
            response_text = result.data if isinstance(result.data, str) else str(result.data)

            # Extract tool calls from result
            tool_calls = []
            if hasattr(result, '_all_messages'):
                for msg in result._all_messages:
                    if hasattr(msg, 'parts'):
                        for part in msg.parts:
                            if hasattr(part, 'tool_name'):
                                tool_calls.append(part.tool_name)

            logger.info(f"🔧 Tools called this attempt: {tool_calls}")

            # Detect hallucination
            is_hallucination = detector.detect_hallucination(response_text, tool_calls)

            if not is_hallucination:
                logger.info("✅ Valid response with real data")
                return response_text

            if attempt < max_retries:
                logger.warning(f"⚠️  Hallucination detected, retrying with stronger prompt...")
            else:
                logger.error(f"❌ Max retries ({max_retries}) reached")
                logger.error(f"   Returning response anyway, but it may contain hallucinated data")
                logger.error(f"   Consider: 1) Simplifying system prompt, 2) Using different LLM model")
                return response_text

        except Exception as e:
            logger.error(f"❌ Error on attempt {attempt}: {e}")
            if attempt >= max_retries:
                raise
            logger.warning(f"   Retrying...")

    return response_text


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events.
    """
    global service_invoker

    # Startup
    logger.info("🚀 Starting Chatbot Agent Service...")
    logger.info("   With Hallucination Detection & Retry Logic")

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
    description="A chatbot that discovers and invokes services dynamically (with hallucination detection)",
    version="2.1.0",
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
        "version": "2.1.0",
        "features": [
            "Generic service invocation",
            "Dynamic service discovery",
            "Hallucination detection & retry",
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
        # Process the query with retry logic
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

    Uses Pydantic AI agent with hallucination detection to:
    1. Understand user intent
    2. Discover appropriate services from catalogue
    3. Invoke services to get real data (with retry if LLM skips this)
    4. Format and return results
    """
    try:
        logger.info(f"🤖 Processing query for user {query.user_id}")

        # Use the retry wrapper to handle hallucinations
        response_text = await chat_with_retry(
            user_query=query.message,
            user_id=query.user_id,
            query_context=query.context,
            max_retries=2  # Will try up to 3 times total
        )

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
    logger.info("With hallucination detection and automatic retry")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )