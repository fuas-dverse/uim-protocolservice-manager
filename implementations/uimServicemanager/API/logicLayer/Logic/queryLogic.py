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

        FIXED: Uses correct field names (service_url, intent_name, etc.)
        """
        logger.info("🔍 Using keyword-based query processing")

        # Extract keywords
        keywords = self._extract_keywords(query)
        logger.info(f"   Extracted keywords: {keywords}")

        if not keywords:
            return QueryResponse(
                query=query,
                response="No meaningful keywords found in your query. Try being more specific.",
                services_found=[],
                intents_found=[],
                success=True,
                error=None,
                mode="keyword"
            )

        # Get ALL services
        all_services = self.serviceDAL.getServices()

        # Score services based on keyword matches
        scored_services = []
        for service in all_services:
            name = service.get('name', '').lower()
            desc = service.get('description', '').lower()

            matches = 0
            for keyword in keywords:
                kw_lower = keyword.lower()
                if kw_lower in name:
                    matches += 2
                if kw_lower in desc:
                    matches += 1

            if matches > 0:
                scored_services.append((service, matches))

        # Sort and take top 5
        scored_services.sort(key=lambda x: x[1], reverse=True)
        services_data = [s[0] for s in scored_services[:5]]

        logger.info(f"📦 Found {len(services_data)} services")

        # Get intents
        all_intents = []
        for service in services_data[:3]:
            intents = service.get('intents', [])
            all_intents.extend(intents)

        logger.info(f"🎯 Found {len(all_intents)} intents")

        # Build response
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

        # Convert to Pydantic models with CORRECT field names
        services_info = []
        for s in services_data:
            service_info = ServiceInfo(
                id=s.get('id', ''),
                name=s.get('name', ''),
                description=s.get('description'),
                service_url=s.get('service_url'),  # ✅ FIXED
                service_logo_url=s.get('service_logo_url'),
                auth_type=s.get('auth_type', 'none'),
                auth_header_name=s.get('auth_header_name'),
                auth_query_param=s.get('auth_query_param'),
                intent_ids=s.get('intent_ids', []),
                intents=[IntentInfo(
                    id=i.get('id', ''),
                    intent_uid=i.get('intent_uid', ''),
                    intent_name=i.get('intent_name', ''),  # ✅ FIXED
                    description=i.get('description'),
                    http_method=i.get('http_method', 'POST'),
                    endpoint_path=i.get('endpoint_path', ''),
                    input_parameters=i.get('input_parameters', []),
                    output_schema=i.get('output_schema'),
                    tags=i.get('tags', []),
                    rateLimit=i.get('rateLimit'),
                    price=i.get('price', 0.0)
                ) for i in s.get('intents', [])]
            )
            services_info.append(service_info)

        intents_info = []
        for i in all_intents:
            intent_info = IntentInfo(
                id=i.get('id', ''),
                intent_uid=i.get('intent_uid', ''),
                intent_name=i.get('intent_name', ''),  # ✅ FIXED
                description=i.get('description'),
                http_method=i.get('http_method', 'POST'),
                endpoint_path=i.get('endpoint_path', ''),
                input_parameters=i.get('input_parameters', []),
                output_schema=i.get('output_schema'),
                tags=i.get('tags', []),
                rateLimit=i.get('rateLimit'),
                price=i.get('price', 0.0)
            )
            intents_info.append(intent_info)

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
        """AI-powered query processing (placeholder)"""
        logger.info("🤖 Using AI-powered query processing")

        # Fallback to keyword for now
        logger.warning("AI mode not fully implemented, using keyword mode")
        return await self._process_query_keyword(query, agent_id, context)

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from query text"""
        stop_words = {
            'find', 'me', 'show', 'get', 'what', 'are', 'the', 'is', 'can',
            'you', 'i', 'a', 'an', 'and', 'or', 'for', 'with', 'that', 'this',
            'have', 'has', 'need', 'want', 'looking', 'search', 'about'
        }

        words = text.lower().split()
        keywords = [
            word.strip('?,!.')
            for word in words
            if len(word) > 3 and word.lower() not in stop_words
        ]

        return keywords