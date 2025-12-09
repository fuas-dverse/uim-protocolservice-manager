"""
Generic Service Invoker - Works with ANY REST API

Reads service/intent metadata from the catalogue and dynamically constructs
HTTP requests. No hardcoding needed for new services!

Special handling for:
- XML responses (arXiv)
- Authentication (API keys)
- Parameter location (query, path, body, header)
"""
import httpx
import xmltodict
import json
import os
from typing import Dict, Any, Optional, List
from loguru import logger


class GenericServiceInvoker:
    """
    Generic service invoker that works with any REST API.

    Uses metadata from the catalogue to construct HTTP requests dynamically.
    """

    def __init__(self, timeout: int = 30):
        self.client = httpx.AsyncClient(timeout=timeout, follow_redirects=True)
        self.timeout = timeout

        # API keys stored in environment or config
        self.api_keys = {
            "openweathermap.org": os.getenv("OPENWEATHER_API_KEY", "demo_key"),  # Replace with real key
        }

    async def close(self):
        """Close the HTTP client"""
        await self.client.close()

    async def invoke(
        self,
        service_metadata: Dict[str, Any],
        intent_metadata: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Invoke a service intent using metadata.

        Args:
            service_metadata: Service info (name, url, auth_type, etc.)
            intent_metadata: Intent info (http_method, endpoint_path, input_parameters, etc.)
            parameters: User-provided parameters

        Returns:
            Dict with service response data

        Raises:
            Exception if service call fails
        """
        service_name = service_metadata.get("name", "Unknown")
        intent_name = intent_metadata.get("intent_name", "unknown")

        logger.info(f"🔧 Invoking {service_name} - {intent_name}")
        logger.info(f"   Parameters: {parameters}")

        # Build the request
        method = intent_metadata.get("http_method", "POST")
        base_url = service_metadata.get("service_url")
        endpoint_path = intent_metadata.get("endpoint_path", "")
        full_url = f"{base_url}{endpoint_path}"

        # Prepare parameters based on location (query, body, header, path)
        query_params = {}
        body_params = {}
        headers = {}
        path_params = {}

        input_params_schema = intent_metadata.get("input_parameters", [])

        for param_schema in input_params_schema:
            param_name = param_schema.get("name")
            location = param_schema.get("location", "body")
            required = param_schema.get("required", True)
            default = param_schema.get("default")

            # Get value from user parameters or use default
            value = parameters.get(param_name, default)

            # Skip if not provided and not required
            if value is None and not required:
                continue

            if value is None and required:
                logger.warning(f"   Missing required parameter: {param_name}")
                continue

            # Route to appropriate location
            if location == "query":
                query_params[param_name] = value
            elif location == "body":
                body_params[param_name] = value
            elif location == "header":
                headers[param_name] = value
            elif location == "path":
                path_params[param_name] = value

        # Add authentication
        auth_type = service_metadata.get("auth_type", "none")
        if auth_type == "api_key":
            api_key = self._get_api_key(service_metadata)
            if api_key:
                auth_header = service_metadata.get("auth_header_name")
                auth_query = service_metadata.get("auth_query_param")

                if auth_query:
                    query_params[auth_query] = api_key
                elif auth_header:
                    headers[auth_header] = api_key

        # Replace path parameters in URL
        for param_name, param_value in path_params.items():
            full_url = full_url.replace(f"{{{param_name}}}", str(param_value))

        logger.info(f"   🌐 {method} {full_url}")
        logger.info(f"   Query: {query_params}")

        try:
            # Make the HTTP request
            if method == "GET":
                response = await self.client.get(full_url, params=query_params, headers=headers)
            elif method == "POST":
                if body_params:
                    response = await self.client.post(full_url, params=query_params, json=body_params, headers=headers)
                else:
                    response = await self.client.post(full_url, params=query_params, headers=headers)
            elif method == "PUT":
                response = await self.client.put(full_url, params=query_params, json=body_params, headers=headers)
            elif method == "DELETE":
                response = await self.client.delete(full_url, params=query_params, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()

            # Parse response based on content type
            content_type = response.headers.get("content-type", "")

            if "xml" in content_type or "atom" in content_type:
                # Parse XML (e.g., arXiv)
                return await self._parse_xml_response(response, service_name, intent_name)
            elif "json" in content_type or response.text.strip().startswith("{"):
                # Parse JSON
                return await self._parse_json_response(response, service_name, intent_name)
            else:
                # Return raw text
                return {
                    "success": True,
                    "data": response.text,
                    "content_type": content_type
                }

        except httpx.HTTPError as e:
            logger.error(f"❌ HTTP error calling {service_name}: {e}")
            raise Exception(f"Failed to call {service_name}: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Error invoking {service_name}: {e}")
            raise Exception(f"Failed to invoke {service_name}: {str(e)}")

    def _get_api_key(self, service_metadata: Dict[str, Any]) -> Optional[str]:
        """Get API key for a service"""
        service_url = service_metadata.get("service_url", "")

        # Extract domain from URL
        for domain, api_key in self.api_keys.items():
            if domain in service_url:
                return api_key

        return None

    async def _parse_xml_response(
        self,
        response: httpx.Response,
        service_name: str,
        intent_name: str
    ) -> Dict[str, Any]:
        """Parse XML response (e.g., from arXiv)"""
        try:
            data = xmltodict.parse(response.text)

            # arXiv-specific parsing
            if "arxiv" in service_name.lower():
                return self._parse_arxiv_response(data, intent_name)

            # Generic XML parsing
            return {
                "success": True,
                "data": data,
                "format": "xml"
            }

        except Exception as e:
            logger.error(f"Failed to parse XML response: {e}")
            raise

    async def _parse_json_response(
        self,
        response: httpx.Response,
        service_name: str,
        intent_name: str
    ) -> Dict[str, Any]:
        """Parse JSON response"""
        try:
            data = response.json()

            # OpenWeather-specific parsing
            if "openweather" in service_name.lower():
                return self._parse_openweather_response(data, intent_name)

            # Generic JSON parsing
            return {
                "success": True,
                "data": data,
                "format": "json"
            }

        except Exception as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise

    def _parse_arxiv_response(self, data: Dict[str, Any], intent_name: str) -> Dict[str, Any]:
        """Parse arXiv XML response into clean format"""
        entries = data.get("feed", {}).get("entry", [])

        # Ensure entries is a list
        if isinstance(entries, dict):
            entries = [entries]

        papers = []
        for entry in entries:
            # Extract authors
            authors_data = entry.get("author", [])
            if isinstance(authors_data, dict):
                authors_data = [authors_data]
            authors = [a.get("name", "Unknown") for a in authors_data]

            # Extract links
            links = entry.get("link", [])
            if isinstance(links, dict):
                links = [links]

            pdf_url = None
            for link in links:
                if link.get("@title") == "pdf":
                    pdf_url = link.get("@href")
                    break

            paper = {
                "id": entry.get("id", "").split("/")[-1],
                "title": entry.get("title", "").strip(),
                "authors": authors,
                "summary": entry.get("summary", "").strip()[:500] + "..." if len(entry.get("summary", "")) > 500 else entry.get("summary", "").strip(),
                "published": entry.get("published", ""),
                "updated": entry.get("updated", ""),
                "pdf_url": pdf_url,
                "categories": [c.get("@term") for c in (entry.get("category", []) if isinstance(entry.get("category", []), list) else [entry.get("category", {})])]
            }
            papers.append(paper)

        logger.info(f"   ✅ Parsed {len(papers)} papers from arXiv")

        return {
            "success": True,
            "papers": papers,
            "total_results": len(papers),
            "format": "arxiv"
        }

    def _parse_openweather_response(self, data: Dict[str, Any], intent_name: str) -> Dict[str, Any]:
        """Parse OpenWeather JSON response into clean format"""

        if intent_name == "get_current_weather":
            # Current weather response
            return {
                "success": True,
                "temperature": data.get("main", {}).get("temp"),
                "feels_like": data.get("main", {}).get("feels_like"),
                "conditions": data.get("weather", [{}])[0].get("description", "Unknown"),
                "humidity": data.get("main", {}).get("humidity"),
                "wind_speed": data.get("wind", {}).get("speed"),
                "city": data.get("name"),
                "country": data.get("sys", {}).get("country"),
                "format": "openweather_current"
            }

        elif intent_name == "get_forecast":
            # Forecast response
            forecast_list = data.get("list", [])
            forecasts = []

            for item in forecast_list[:8]:  # Next 24 hours (3-hour intervals)
                forecasts.append({
                    "datetime": item.get("dt_txt"),
                    "temperature": item.get("main", {}).get("temp"),
                    "conditions": item.get("weather", [{}])[0].get("description"),
                    "wind_speed": item.get("wind", {}).get("speed")
                })

            return {
                "success": True,
                "city": data.get("city", {}).get("name"),
                "forecasts": forecasts,
                "format": "openweather_forecast"
            }

        # Generic OpenWeather response
        return {
            "success": True,
            "data": data,
            "format": "openweather"
        }