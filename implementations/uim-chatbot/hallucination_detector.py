"""
Chatbot Wrapper with Hallucination Detection

This wrapper detects when the LLM responds without calling invoke_service
and automatically retries with a more forceful prompt.
"""
import httpx
from pydantic_ai import Agent, RunContext
from dataclasses import dataclass
from typing import Dict, Any
from loguru import logger

from service_invoker import GenericServiceInvoker
from agent import chatbot_agent, AgentDependencies


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
            "I found" in response and not invoke_called,
            "Lost in the Middle" in response,  # Known hallucinated paper title
        ]
        
        if any(hallucination_indicators):
            logger.warning(f"⚠️  HALLUCINATION DETECTED: Response has indicators")
            logger.warning(f"   Response preview: {response[:200]}")
            return True
        
        return False


async def chat_with_retry(
    user_query: str,
    service_invoker: GenericServiceInvoker,
    query_context: Dict[str, Any] = None,
    max_retries: int = 2
) -> str:
    """
    Run chatbot with automatic retry on hallucination detection
    
    Args:
        user_query: User's question
        service_invoker: Service invoker instance
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
            # Make the prompt more forceful
            query_with_hint = f"{user_query}\n\nIMPORTANT: You MUST call invoke_service to get real data. Do NOT respond without calling it."
        else:
            query_with_hint = user_query
        
        try:
            # Run the agent
            result = await chatbot_agent.run(query_with_hint, deps=deps)
            response_text = result.data if isinstance(result.data, str) else str(result.data)
            
            # Check for hallucination
            tool_calls = []
            if hasattr(result, '_all_messages'):
                for msg in result._all_messages:
                    if hasattr(msg, 'parts'):
                        for part in msg.parts:
                            if hasattr(part, 'tool_name'):
                                tool_calls.append(part.tool_name)
            
            logger.info(f"🔧 Tools called: {tool_calls}")
            
            # Detect hallucination
            is_hallucination = detector.detect_hallucination(response_text, tool_calls)
            
            if not is_hallucination:
                logger.info("✅ Valid response with real data")
                return response_text
            
            if attempt < max_retries:
                logger.warning(f"⚠️  Hallucination detected, retrying...")
            else:
                logger.error(f"❌ Max retries reached, returning response anyway")
                logger.error(f"   Response may contain hallucinated data!")
                return response_text
                
        except Exception as e:
            logger.error(f"❌ Error on attempt {attempt}: {e}")
            if attempt >= max_retries:
                raise
    
    return response_text


# Example usage in main.py:
"""
async def process_chat_query(query: ChatbotQuery) -> ChatbotResponse:
    try:
        # Use the wrapper instead of direct agent call
        response_text = await chat_with_retry(
            user_query=query.message,
            service_invoker=service_invoker,
            query_context=query.context,
            max_retries=2
        )
        
        return ChatbotResponse(
            user_id=query.user_id,
            message=response_text,
            query=query.message,
            services_discovered=[],
            service_invocation=None,
            success=True
        )
        
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        return ChatbotResponse(
            user_id=query.user_id,
            message=f"I encountered an error: {str(e)}",
            query=query.message,
            success=False,
            error=str(e)
        )
"""
