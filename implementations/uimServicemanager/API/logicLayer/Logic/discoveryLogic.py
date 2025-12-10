"""
Discovery Logic - LLM-based service selection

Handles intelligent service discovery using intent tags and descriptions.
Uses Ollama with llama3.2 for service selection based on user queries.
"""
from typing import Dict, Any, List, Optional
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
        # 1. Get all services with their intents
        services = self.serviceDAL.getServices()
        
        if not services:
            raise ValueError("No services available in catalogue")

        # 2. Build service summaries with tags from intents
        service_summaries = self._build_service_summaries(services)

        # 3. Call LLM to select service
        selected_name = await self._call_llm_for_selection(user_query, service_summaries)

        # 4. Find the service (with fuzzy matching)
        selected_service = self._find_service_by_name(services, selected_name)

        if not selected_service:
            raise ValueError(
                f"LLM selected unknown service: '{selected_name}'. "
                f"Available: {[s['name'] for s in services]}"
            )

        logger.info(f"🎯 Discovery: Selected '{selected_service['name']}' for query: '{user_query}'")
        return selected_service

    def _build_service_summaries(self, services: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Build summaries of services with aggregated tags from their intents.

        Returns list of dicts: {name, description, tags, intent_names}
        """
        summaries = []

        for service in services:
            # Aggregate all tags from intents
            all_tags = set()
            intent_names = []

            for intent in service.get("intents", []):
                intent_names.append(intent.get("intent_name", ""))
                tags = intent.get("tags", [])
                all_tags.update(tags)

            summaries.append({
                "name": service["name"],
                "description": service.get("description", ""),
                "tags": list(all_tags),
                "intent_names": intent_names
            })

        return summaries

    async def _call_llm_for_selection(
        self, 
        user_query: str, 
        service_summaries: List[Dict[str, Any]]
    ) -> str:
        """
        Call Ollama LLM to select the most appropriate service.

        Returns the service name selected by the LLM.
        """
        # Format services for LLM
        service_descriptions = []
        for svc in service_summaries:
            tags_str = ", ".join(svc["tags"]) if svc["tags"] else "no tags"
            intents_str = ", ".join(svc["intent_names"]) if svc["intent_names"] else "no intents"
            service_descriptions.append(
                f"- {svc['name']}: {svc['description']} [Tags: {tags_str}] [Intents: {intents_str}]"
            )

        available_services = "\n".join(service_descriptions)

        # Build prompt
        prompt = f"""ctx: User Question: {user_query}
available services:
{available_services}

Question: Please select the service that is most appropriate to answer the User question and return the service name in the following format: {{answer: service_name}}

Only return the JSON object, nothing else."""

        # Call Ollama
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
                
                result = response.json()
                llm_response = result.get("response", "")
                
                logger.debug(f"LLM raw response: {llm_response}")
                
                # Parse the response
                selected_name = self._parse_llm_response(llm_response)
                logger.info(f"🤖 LLM selected: {selected_name}")
                return selected_name

        except httpx.HTTPError as e:
            logger.error(f"❌ Ollama API error: {e}")
            raise RuntimeError(f"Failed to call LLM: {e}")

    def _parse_llm_response(self, llm_response: str) -> str:
        """
        Parse LLM response to extract service name.

        Handles various formats:
        - {answer: Service Name}
        - {"answer": "Service Name"}
        - answer: Service Name
        - Service Name
        """
        # Try JSON parsing first
        try:
            # Clean markdown code blocks if present
            clean = llm_response.strip().strip('`').strip()
            if clean.startswith('json'):
                clean = clean[4:].strip()
            
            parsed = json.loads(clean)
            if isinstance(parsed, dict) and "answer" in parsed:
                return parsed["answer"].strip()
        except (json.JSONDecodeError, KeyError):
            pass

        # Try regex extraction for {answer: X} or {"answer": "X"} format
        match = re.search(
            r'\{?\s*["\']?answer["\']?\s*:\s*["\']?([^"\'}\n]+)["\']?\s*\}?',
            llm_response,
            re.IGNORECASE
        )
        if match:
            return match.group(1).strip()

        # Last resort: return first line, cleaned
        first_line = llm_response.split('\n')[0].strip()
        cleaned = first_line.strip('{}').strip('"').strip("'").strip()
        
        logger.warning(f"⚠️  Using fallback parsing, extracted: {cleaned}")
        return cleaned

    def _find_service_by_name(
        self, 
        services: List[Dict[str, Any]], 
        name_query: str
    ) -> Optional[Dict[str, Any]]:
        """
        Find service by name with fuzzy matching.

        Tries:
        1. Exact match (case-insensitive)
        2. Partial match (name contains query or vice versa)
        3. Fuzzy match using difflib
        """
        from difflib import get_close_matches

        name_lower = name_query.lower()

        # Exact match (case-insensitive)
        for service in services:
            if service["name"].lower() == name_lower:
                logger.debug(f"✅ Exact match found: {service['name']}")
                return service

        # Partial match (contains)
        for service in services:
            service_name_lower = service["name"].lower()
            if name_lower in service_name_lower or service_name_lower in name_lower:
                logger.debug(f"✅ Partial match found: {service['name']}")
                return service

        # Fuzzy match
        service_names = [s["name"] for s in services]
        matches = get_close_matches(name_query, service_names, n=1, cutoff=0.6)

        if matches:
            matched_name = matches[0]
            logger.debug(f"✅ Fuzzy match found: {matched_name} (from '{name_query}')")
            return next(s for s in services if s["name"] == matched_name)

        logger.warning(f"❌ No match found for: {name_query}")
        return None
