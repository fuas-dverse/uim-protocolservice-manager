"""
Service Invoker - Executes calls to external services.

This module takes service metadata from the catalogue and actually invokes
the external API, returning real results.
"""
import httpx
import xmltodict
from typing import Dict, Any, Optional, List
from loguru import logger


class ServiceInvoker:
    """
    Invokes external services based on catalogue metadata.
    
    Currently supports:
    - arXiv API (XML-based)
    
    Can be extended to support other service types.
    """
    
    def __init__(self, timeout: int = 30):
        self.client = httpx.AsyncClient(timeout=timeout, follow_redirects=True)
        self.timeout = timeout

    async def close(self):
        """Close the HTTP client"""
        await self.client.close()

    async def invoke(
        self,
        service_name: str,
        service_url: str,
        intent_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Invoke an external service intent.

        Args:
            service_name: Name of the service (e.g., "arXiv API")
            service_url: Base URL of the service
            intent_name: Intent to invoke (e.g., "search_papers")
            parameters: Parameters for the intent

        Returns:
            Dict with service response data

        Raises:
            Exception if service call fails
        """
        logger.info(f"Invoking {service_name} - {intent_name} with params: {parameters}")

        # Route to appropriate handler based on service
        if "arxiv" in service_name.lower():
            return await self._invoke_arxiv(intent_name, parameters)
        else:
            raise NotImplementedError(f"Service '{service_name}' not yet supported")

    async def _invoke_arxiv(
        self,
        intent_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Invoke arXiv API intents.

        arXiv API docs: https://info.arxiv.org/help/api/index.html
        """
        base_url = "https://export.arxiv.org/api/query"

        if intent_name == "search_papers":
            return await self._arxiv_search_papers(base_url, parameters)
        elif intent_name == "get_paper_details":
            return await self._arxiv_get_paper_details(base_url, parameters)
        elif intent_name == "get_recent_papers":
            return await self._arxiv_get_recent_papers(base_url, parameters)
        else:
            raise NotImplementedError(f"arXiv intent '{intent_name}' not implemented")

    async def _arxiv_search_papers(
        self,
        base_url: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Search for papers on arXiv.

        Parameters:
            query: Search query string (e.g., "multi-agent systems")
            max_results: Maximum number of results (default: 10)
            sort_by: Sort order - "relevance", "lastUpdatedDate", "submittedDate"
        """
        query = parameters.get("query", "")
        max_results = parameters.get("max_results", 10)
        sort_by = parameters.get("sort_by", "relevance")

        if not query:
            raise ValueError("Query parameter is required for search_papers")

        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
            "sortBy": sort_by,
            "sortOrder": "descending"
        }

        logger.info(f"Searching arXiv with params: {params}")

        try:
            response = await self.client.get(base_url, params=params)
            response.raise_for_status()

            # Parse XML response
            data = xmltodict.parse(response.text)

            # Extract entries
            entries = data.get("feed", {}).get("entry", [])

            # Ensure entries is a list (single result returns dict)
            if isinstance(entries, dict):
                entries = [entries]

            # Parse papers
            papers = []
            for entry in entries:
                paper = self._parse_arxiv_entry(entry)
                papers.append(paper)

            logger.info(f"Found {len(papers)} papers")

            return {
                "papers": papers,
                "total_results": len(papers),
                "query": query
            }

        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling arXiv: {e}")
            raise Exception(f"Failed to search arXiv: {str(e)}")
        except Exception as e:
            logger.error(f"Error parsing arXiv response: {e}")
            raise Exception(f"Failed to parse arXiv response: {str(e)}")

    async def _arxiv_get_paper_details(
        self,
        base_url: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get details for a specific paper by arXiv ID.

        Parameters:
            arxiv_id: arXiv paper ID (e.g., "2301.12345")
        """
        arxiv_id = parameters.get("arxiv_id", "")

        if not arxiv_id:
            raise ValueError("arxiv_id parameter is required")

        params = {
            "id_list": arxiv_id
        }

        logger.info(f"Fetching arXiv paper: {arxiv_id}")

        try:
            response = await self.client.get(base_url, params=params)
            response.raise_for_status()

            data = xmltodict.parse(response.text)
            entry = data.get("feed", {}).get("entry", {})

            if not entry:
                raise Exception(f"Paper {arxiv_id} not found")

            paper = self._parse_arxiv_entry(entry)

            return {
                "paper": paper,
                "arxiv_id": arxiv_id
            }

        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling arXiv: {e}")
            raise Exception(f"Failed to fetch paper: {str(e)}")
        except Exception as e:
            logger.error(f"Error parsing arXiv response: {e}")
            raise Exception(f"Failed to parse paper details: {str(e)}")

    async def _arxiv_get_recent_papers(
        self,
        base_url: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get recent papers in a category.

        Parameters:
            category: arXiv category (e.g., "cs.AI", "cs.MA")
            max_results: Maximum number of results (default: 10)
        """
        category = parameters.get("category", "cs.AI")
        max_results = parameters.get("max_results", 10)

        params = {
            "search_query": f"cat:{category}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending"
        }

        logger.info(f"Fetching recent papers in category: {category}")

        try:
            response = await self.client.get(base_url, params=params)
            response.raise_for_status()

            data = xmltodict.parse(response.text)
            entries = data.get("feed", {}).get("entry", [])

            if isinstance(entries, dict):
                entries = [entries]

            papers = []
            for entry in entries:
                paper = self._parse_arxiv_entry(entry)
                papers.append(paper)

            logger.info(f"Found {len(papers)} recent papers")

            return {
                "papers": papers,
                "category": category,
                "total_results": len(papers)
            }

        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling arXiv: {e}")
            raise Exception(f"Failed to fetch recent papers: {str(e)}")
        except Exception as e:
            logger.error(f"Error parsing arXiv response: {e}")
            raise Exception(f"Failed to parse response: {str(e)}")

    def _parse_arxiv_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Parse an arXiv entry into a clean dict"""
        # Extract authors
        authors_data = entry.get("author", [])
        if isinstance(authors_data, dict):
            authors_data = [authors_data]

        authors = [
            author.get("name", "Unknown")
            for author in authors_data
        ]

        # Extract categories
        categories_data = entry.get("category", [])
        if isinstance(categories_data, dict):
            categories_data = [categories_data]

        categories = [
            cat.get("@term", "")
            for cat in categories_data
        ]

        return {
            "title": entry.get("title", "").strip(),
            "authors": authors,
            "summary": entry.get("summary", "").strip(),
            "arxiv_id": entry.get("id", "").split("/")[-1],
            "published": entry.get("published", ""),
            "updated": entry.get("updated", ""),
            "categories": categories,
            "pdf_url": entry.get("id", "").replace("/abs/", "/pdf/") + ".pdf",
            "abs_url": entry.get("id", "")
        }