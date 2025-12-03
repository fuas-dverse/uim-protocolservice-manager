import httpx
from typing import List, Optional, Dict, Any
from loguru import logger


class CatalogueClient:

    def __init__(self, base_url: str, timeout: float = 10.0):
        """
        Initialize the catalogue client.

        Args:
            base_url: Base URL of the catalogue API (e.g., http://localhost:8000)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=timeout, follow_redirects=True)
        logger.info(f"CatalogueClient initialized with base_url: {base_url}")

    async def close(self):
        await self.client.aclose()

    async def search_services(
            self,
            query: Optional[str] = None,
            limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for services in the catalogue.

        Args:
            query: Search query (searches in name and description)
            limit: Maximum number of results

        Returns:
            List of service dictionaries
        """
        try:
            params = {}
            if query:
                params["name"] = query  # Backend uses 'name' parameter, not 'search'

            response = await self.client.get(
                f"{self.base_url}/services",
                params=params
            )
            response.raise_for_status()

            services = response.json()
            logger.info(f"Found {len(services)} services for query: {query}")
            return services

        except httpx.HTTPError as e:
            logger.error(f"Error searching services: {e}")
            return []

    async def get_service_by_id(self, service_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific service by ID.

        Args:
            service_id: Service ID

        Returns:
            Service dictionary or None if not found
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/services/{service_id}"
            )
            response.raise_for_status()

            service = response.json()
            logger.info(f"Retrieved service: {service.get('name')}")
            return service

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Service not found: {service_id}")
                return None
            logger.error(f"Error getting service: {e}")
            return None

    async def get_service_intents(
            self,
            service_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get all intents for a specific service.

        Args:
            service_id: Service ID

        Returns:
            List of intent dictionaries
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/services/{service_id}/intents"
            )
            response.raise_for_status()

            intents = response.json()
            logger.info(f"Found {len(intents)} intents for service: {service_id}")
            return intents

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                # Intent endpoint doesn't exist for this backend - that's okay
                logger.debug(f"Intent endpoint not available for service: {service_id}")
                return []
            logger.error(f"Error getting intents: {e}")
            return []
        except httpx.HTTPError as e:
            logger.error(f"Error getting intents: {e}")
            return []

    async def search_intents(
            self,
            query: Optional[str] = None,
            service_id: Optional[str] = None,
            limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for intents across all services.

        Args:
            query: Search query (searches in name and description)
            service_id: Filter by specific service
            limit: Maximum number of results

        Returns:
            List of intent dictionaries
        """
        try:
            params = {"limit": limit}
            if query:
                params["search"] = query
            if service_id:
                params["service_id"] = service_id

            response = await self.client.get(
                f"{self.base_url}/intents",
                params=params
            )
            response.raise_for_status()

            intents = response.json()
            logger.info(f"Found {len(intents)} intents for query: {query}")
            return intents

        except httpx.HTTPError as e:
            logger.error(f"Error searching intents: {e}")
            return []

    async def health_check(self) -> bool:
        """
        Check if the catalogue API is healthy.

        Returns:
            True if healthy, False otherwise
        """
        try:
            response = await self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False