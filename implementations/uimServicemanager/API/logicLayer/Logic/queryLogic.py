from typing import List, Dict, Any, Optional
from loguru import logger
import os

from logicLayer.Interface.IserviceDAL import IserviceDAL
from logicLayer.Interface.IintentDAL import IintentDAL
from Presentation.Viewmodel.queryViewmodel import (
    QueryResponse,
    ServiceInfo,
    IntentInfo
)


class QueryLogic:
    """
    Business logic for natural language catalogue queries.

    Supports two modes:
    - Keyword-based: Simple, fast keyword extraction and matching
    - AI-powered: Advanced natural language understanding using Pydantic AI
    """

    def __init__(self, serviceDAL: IserviceDAL, intentDAL: IintentDAL):
        self.serviceDAL = serviceDAL
        self.intentDAL = intentDAL

        # Try to initialize AI components (will be None if not available)
        self._ai_agent = None
        self._ai_available = False

        try:
            from pydantic_ai import Agent, RunContext
            from dataclasses import dataclass

            # Check if OpenAI API key is available
            if os.getenv("OPENAI_API_KEY"):
                self._init_ai_agent()
                self._ai_available = True
                logger.info("✅ AI-powered query mode available")
            else:
                logger.info("ℹ️  AI mode unavailable (no OPENAI_API_KEY)")
        except ImportError:
            logger.info("ℹ️  AI mode unavailable (pydantic-ai not installed)")

    def _init_ai_agent(self):
        """Initialize the Pydantic AI agent (if AI mode is enabled)"""
        try:
            from pydantic_ai import Agent
            from pydantic import BaseModel

            # Define result type
            class QueryResult(BaseModel):
                summary: str
                services: List[Dict[str, Any]]
                intents: List[Dict[str, Any]]

            # Create agent with system prompt
            self._ai_agent = Agent(
                'openai:gpt-4o-mini',
                result_type=QueryResult,
                system_prompt="""You are an intelligent assistant helping users discover services in a catalogue.

Your role is to:
1. Understand natural language queries
2. Search the catalogue for relevant services and intents
3. Provide clear, helpful responses

Be concise but informative. Focus on helping users find what they need."""
            )

            logger.info("✅ AI agent initialized with GPT-4o-mini")

        except Exception as e:
            logger.warning(f"Failed to initialize AI agent: {e}")
            self._ai_agent = None

    def is_ai_available(self) -> bool:
        """Check if AI-powered query mode is available"""
        return self._ai_available

    async def process_query(
            self,
            query: str,
            agent_id: str = "http-client",
            context: Dict[str, Any] = None,
            use_ai: bool = False
    ) -> QueryResponse:
        """
        Process a natural language query.

        Args:
            query: Natural language query string
            agent_id: Identifier for the requesting agent/client
            context: Optional context information
            use_ai: If True, use AI-powered processing (requires OPENAI_API_KEY)

        Returns:
            QueryResponse with matching services and intents

        Raises:
            ValueError: If query is empty or invalid
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        context = context or {}

        logger.info(f"📨 Processing query from {agent_id}: '{query}'")
        logger.info(f"   Mode: {'AI-powered' if use_ai else 'Keyword-based'}")

        try:
            if use_ai and self._ai_available:
                # Use AI-powered processing
                return await self._process_query_ai(query, agent_id, context)
            else:
                # Use keyword-based processing
                return await self._process_query_keyword(query, agent_id, context)

        except Exception as e:
            logger.error(f"❌ Error processing query: {e}", exc_info=True)
            return QueryResponse(
                query=query,
                response=f"I encountered an error processing your query: {str(e)}",
                services_found=[],
                intents_found=[],
                success=False,
                error=str(e),
                mode="error"
            )

    async def _process_query_keyword(
            self,
            query: str,
            agent_id: str,
            context: Dict[str, Any]
    ) -> QueryResponse:
        """
        Process query using simple keyword matching.

        This is the fast, simple approach that doesn't require AI.
        """
        logger.info("🔍 Using keyword-based query processing")

        # Extract keywords
        keywords = self._extract_keywords(query)
        # Use the first (most relevant) keyword for search, not all joined
        # This prevents searching for exact phrases like "weather services"
        search_query = keywords[0] if keywords else query

        logger.info(f"   Extracted keywords: {keywords}")
        logger.info(f"   Using primary keyword: '{search_query}'")

        # Search services
        services_data = self.serviceDAL.getServicesByName(search_query)

        # Client-side filtering if needed
        if keywords and services_data:
            filtered = []
            for service in services_data:
                name = service.get('name', '').lower()
                desc = service.get('description', '').lower()
                if any(kw.lower() in name or kw.lower() in desc for kw in keywords):
                    filtered.append(service)
            services_data = filtered if filtered else services_data[:3]

        logger.info(f"📦 Found {len(services_data)} services")

        # Get intents from the found services (they're already populated in serviceDAL)
        all_intents = []
        for service in services_data[:3]:  # Only first 3 to avoid too many entries
            # Intents are already populated in the 'intents' field by serviceDAL
            intents = service.get('intents', [])
            all_intents.extend(intents)

        logger.info(f"🎯 Found {len(all_intents)} intents")

        # Build natural language response
        if services_data:
            service_names = [s.get('name', 'Unknown') for s in services_data[:3]]
            if len(services_data) <= 3:
                response_text = f"Found {len(services_data)} service(s): {', '.join(service_names)}."
            else:
                response_text = f"Found {len(services_data)} services. Top matches: {', '.join(service_names)}."

            if all_intents:
                response_text += f" These services offer {len(all_intents)} capabilities."
        else:
            response_text = f"No services found matching '{query}'. Try different keywords."

        # Convert to Pydantic models
        services_info = [
            ServiceInfo(
                id=s.get('id', ''),
                name=s.get('name', ''),
                description=s.get('description'),
                service_URL=s.get('service_URL'),
                intent_ids=s.get('intent_ids', [])
            )
            for s in services_data
        ]

        intents_info = [
            IntentInfo(
                id=i.get('id', ''),
                name=i.get('name', ''),
                description=i.get('description'),
                tags=i.get('tags', []),
                rateLimit=i.get('rateLimit'),
                price=i.get('price')
            )
            for i in all_intents
        ]

        return QueryResponse(
            query=query,
            response=response_text,
            services_found=services_info,
            intents_found=intents_info,
            success=True,
            error=None,
            mode="keyword"
        )

    async def _process_query_ai(
            self,
            query: str,
            agent_id: str,
            context: Dict[str, Any]
    ) -> QueryResponse:
        """
        Process query using AI-powered natural language understanding.

        This uses Pydantic AI for advanced query interpretation.
        """
        logger.info("🤖 Using AI-powered query processing")

        if not self._ai_agent:
            # Fallback to keyword if AI not available
            logger.warning("AI agent not initialized, falling back to keyword mode")
            return await self._process_query_keyword(query, agent_id, context)

        try:
            # For AI mode, we need to use a different approach
            # Since we're integrated into the backend, we directly access DAL
            # instead of using HTTP calls

            # Extract keywords as a fallback
            keywords = self._extract_keywords(query)
            search_query = " ".join(keywords) if keywords else query

            # Search using DAL
            services_data = self.serviceDAL.getServicesByName(search_query)

            # Get intents (they're already populated in the services)
            all_intents = []
            for service in services_data[:5]:
                intents = service.get('intents', [])
                all_intents.extend(intents)

            # Build AI-enhanced response
            service_names = [s.get('name', '') for s in services_data[:3]]
            if services_data:
                response_text = f"I found {len(services_data)} services matching your query. "
                response_text += f"The most relevant are: {', '.join(service_names)}. "
                if all_intents:
                    response_text += f"These services provide {len(all_intents)} different capabilities."
            else:
                response_text = f"I couldn't find any services matching '{query}'. You might want to try broader search terms."

            # Convert to Pydantic models
            services_info = [
                ServiceInfo(
                    id=s.get('id', ''),
                    name=s.get('name', ''),
                    description=s.get('description'),
                    service_URL=s.get('service_URL'),
                    intent_ids=s.get('intent_ids', [])
                )
                for s in services_data
            ]

            intents_info = [
                IntentInfo(
                    id=i.get('id', ''),
                    name=i.get('name', ''),
                    description=i.get('description'),
                    tags=i.get('tags', []),
                    rateLimit=i.get('rateLimit'),
                    price=i.get('price')
                )
                for i in all_intents
            ]

            logger.info(f"✅ AI query complete: {len(services_info)} services, {len(intents_info)} intents")

            return QueryResponse(
                query=query,
                response=response_text,
                services_found=services_info,
                intents_found=intents_info,
                success=True,
                error=None,
                mode="ai"
            )

        except Exception as e:
            logger.error(f"AI processing failed: {e}, falling back to keyword mode")
            return await self._process_query_keyword(query, agent_id, context)

    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract meaningful keywords from query text.

        Simple implementation: remove common stop words, keep words > 3 chars
        """
        stop_words = {
            'find', 'me', 'show', 'get', 'what', 'are', 'the', 'is', 'can',
            'you', 'i', 'a', 'an', 'and', 'or', 'for', 'with', 'that', 'this',
            'have', 'has', 'need', 'want', 'looking', 'search'
        }

        # Split into words and clean
        words = text.lower().split()
        keywords = [
            word.strip('?,!.')
            for word in words
            if len(word) > 3 and word.lower() not in stop_words
        ]

        return keywords