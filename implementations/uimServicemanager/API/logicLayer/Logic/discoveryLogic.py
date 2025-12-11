"""
Discovery Logic

Implements LLM-based intelligent service discovery by analyzing user queries
and matching them against service capabilities using Ollama.
"""
from typing import Dict, Any, List
from logicLayer.Interface.IserviceDAL import IserviceDAL
import httpx
import json
import re
from loguru import logger


class DiscoveryLogic:
    """Business logic for LLM-based service discovery"""

    def __init__(self, serviceDAL: IserviceDAL, ollama_base_url: str = "http://localhost:11434"):
        self.serviceDAL = serviceDAL
        self.ollama_base_url = ollama_base_url

    async def discover_service(self, user_query: str) -> Dict[str, Any]:
        """
        Discover the most appropriate service for a user query using LLM.

        Args:
            user_query: Natural language query from user

        Returns:
            Full service object with intents

        Raises:
            ValueError: If no appropriate service found
            RuntimeError: If LLM call fails
        """
        services = self.serviceDAL.getServices()

        if not services:
            raise ValueError("No services available in catalogue")

        service_summaries = self._build_service_summaries(services)
        selected_name = await self._call_llm_for_selection(user_query, service_summaries)
        selected_service = self._find_service_by_name(services, selected_name)

        if not selected_service:
            raise ValueError(
                f"LLM selected unknown service: '{selected_name}'. "
                f"Available: {[s['name'] for s in services]}"
            )

        logger.info(f"🎯 Discovery: Selected '{selected_service['name']}' for query: '{user_query}'")
        return selected_service

    def _build_service_summaries(self, services: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build summaries of services with aggregated tags from their intents"""
        summaries = []

        for service in services:
            all_tags = set()
            intent_names = []

            for intent in service.get("intents", []):
                all_tags.update(intent.get("tags", []))
                intent_names.append(intent.get("intent_name", ""))

            summaries.append({
                "name": service.get("name"),
                "description": service.get("description", ""),
                "tags": list(all_tags),
                "intent_count": len(service.get("intents", [])),
                "intent_names": intent_names
            })

        return summaries

    async def _call_llm_for_selection(
        self,
        user_query: str,
        service_summaries: List[Dict[str, Any]]
    ) -> str:
        """
        Call Ollama LLM to select the best service for the query.

        Returns:
            Name of the selected service

        Raises:
            RuntimeError: If LLM call fails
        """
        summaries_text = "\n".join([
            f"- {s['name']}: {s['description'][:100]}... Tags: {', '.join(s['tags'][:5])}"
            for s in service_summaries
        ])

        prompt = f"""You are a service discovery assistant. Given a user's query, select the MOST appropriate service from the list below.

USER QUERY: "{user_query}"

AVAILABLE SERVICES:
{summaries_text}

INSTRUCTIONS:
1. Analyze which service best matches the user's intent
2. Consider the service descriptions and tags
3. Return ONLY the exact service name, nothing else
4. Do not add quotes, explanations, or extra text

YOUR RESPONSE (service name only):"""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.ollama_base_url}/api/generate",
                    json={
                        "model": "llama3.2",
                        "prompt": prompt,
                        "stream": False
                    }
                )
                response.raise_for_status()

                data = response.json()
                selected_name = data.get("response", "").strip()

                selected_name = re.sub(r'^["\']|["\']$', '', selected_name)
                selected_name = selected_name.split('\n')[0].strip()

                logger.info(f"🤖 LLM selected: '{selected_name}'")
                return selected_name

        except httpx.HTTPError as e:
            logger.error(f"Failed to call Ollama: {e}")
            raise RuntimeError(f"LLM service unavailable: {str(e)}")
        except Exception as e:
            logger.error(f"Error during LLM call: {e}")
            raise RuntimeError(f"LLM call failed: {str(e)}")

    def _find_service_by_name(
        self,
        services: List[Dict[str, Any]],
        name_query: str
    ) -> Dict[str, Any]:
        """
        Find a service by name with fuzzy matching.

        Tries exact match, partial match, then fuzzy match.
        """
        from difflib import get_close_matches

        name_lower = name_query.lower()

        for service in services:
            if service["name"].lower() == name_lower:
                logger.debug(f"✅ Exact match found: {service['name']}")
                return service

        for service in services:
            service_name_lower = service["name"].lower()
            if name_lower in service_name_lower or service_name_lower in name_lower:
                logger.debug(f"✅ Partial match found: {service['name']}")
                return service

        service_names = [s["name"] for s in services]
        matches = get_close_matches(name_query, service_names, n=1, cutoff=0.6)

        if matches:
            matched_name = matches[0]
            logger.debug(f"✅ Fuzzy match found: {matched_name} (from '{name_query}')")
            return next(s for s in services if s["name"] == matched_name)

        logger.warning(f"❌ No match found for: {name_query}")
        return None