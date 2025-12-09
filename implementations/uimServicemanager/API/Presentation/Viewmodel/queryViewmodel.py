"""
Query Viewmodel - Updated to return full service metadata

The chatbot needs complete metadata to invoke services dynamically.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class IntentInfo(BaseModel):
    """
    Intent information with FULL invocation metadata.

    This is what the chatbot needs to call the service!
    """
    id: str
    intent_uid: str
    intent_name: str
    description: Optional[str] = None

    # API Invocation details
    http_method: str = "POST"
    endpoint_path: str
    input_parameters: List[Dict[str, Any]] = Field(default_factory=list)
    output_schema: Optional[Dict[str, Any]] = None

    # Metadata
    tags: List[str] = Field(default_factory=list)
    rateLimit: Optional[int] = None
    price: float = 0.0


class ServiceInfo(BaseModel):
    """
    Service information with FULL metadata for invocation.

    Includes auth details the chatbot needs.
    """
    id: str
    name: str
    description: Optional[str] = None

    # Service URLs
    service_url: str
    service_logo_url: Optional[str] = None

    # Authentication (chatbot needs this!)
    auth_type: Optional[str] = "none"
    auth_header_name: Optional[str] = None
    auth_query_param: Optional[str] = None

    # Intents with full metadata
    intent_ids: List[str] = Field(default_factory=list)
    intents: List[IntentInfo] = Field(default_factory=list)

    # UIM endpoints
    uim_api_discovery: Optional[str] = None
    uim_api_execute: Optional[str] = None


class QueryRequest(BaseModel):
    """Request model for natural language query"""
    query: str = Field(..., min_length=1, max_length=500, description="Natural language query")
    agent_id: Optional[str] = Field("http-client", description="ID of requesting agent")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Optional context")
    use_ai: bool = Field(False, description="Use AI-powered query processing (requires OPENAI_API_KEY)")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Find weather services",
                "agent_id": "chatbot-agent-1",
                "context": {},
                "use_ai": False
            }
        }


class QueryResponse(BaseModel):
    """
    Response model for query endpoint.

    Returns FULL service metadata so chatbot can invoke directly!
    """
    query: str
    response: str = Field(..., description="Natural language response")

    # Full service metadata (not just names!)
    services_found: List[ServiceInfo] = Field(default_factory=list)
    intents_found: List[IntentInfo] = Field(default_factory=list)

    success: bool
    error: Optional[str] = None
    mode: str = Field("keyword", description="Processing mode: 'keyword' or 'ai'")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "query": "weather in London",
                "response": "Found 1 service: OpenWeather API",
                "services_found": [{
                    "id": "507f1f77bcf86cd799439011",
                    "name": "OpenWeather API",
                    "description": "Weather data and forecasts",
                    "service_url": "https://api.openweathermap.org/data/2.5",
                    "auth_type": "api_key",
                    "auth_query_param": "appid",
                    "intents": [{
                        "id": "intent_123",
                        "intent_uid": "openweather:getCurrentWeather:v1",
                        "intent_name": "get_current_weather",
                        "http_method": "GET",
                        "endpoint_path": "/weather",
                        "input_parameters": [
                            {
                                "name": "q",
                                "type": "string",
                                "required": True,
                                "location": "query"
                            }
                        ],
                        "tags": ["weather", "current"]
                    }]
                }],
                "success": True,
                "error": None,
                "mode": "keyword"
            }
        }