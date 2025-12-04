from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ServiceInfo(BaseModel):
    """Information about a service from the catalogue"""
    id: str
    name: str
    description: Optional[str] = None
    service_URL: Optional[str] = None
    intent_ids: List[str] = Field(default_factory=list)


class IntentInfo(BaseModel):
    """Information about an intent/capability of a service"""
    id: str
    name: str
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    rateLimit: Optional[int] = None
    price: Optional[float] = None


class QueryRequest(BaseModel):
    """
    Request model for natural language queries.
    
    Used for HTTP POST /query endpoint.
    """
    query: str = Field(
        ...,
        description="Natural language query",
        min_length=1,
        examples=["Find me weather services", "Show services that process payments"]
    )
    agent_id: Optional[str] = Field(
        default="http-client",
        description="Optional identifier for the requesting agent/client"
    )
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional context information (e.g., previous queries, user preferences)"
    )
    use_ai: bool = Field(
        default=False,
        description="If True, use AI-powered query processing (requires OPENAI_API_KEY). If False, use keyword matching."
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Find me weather services with forecasting",
                "agent_id": "web-app-001",
                "context": {"location": "Europe"},
                "use_ai": False
            }
        }


class QueryResponse(BaseModel):
    """
    Response model for natural language queries.
    
    Returned by HTTP POST /query endpoint.
    """
    query: str = Field(..., description="Original query from the request")
    response: str = Field(..., description="Natural language response explaining the results")
    services_found: List[ServiceInfo] = Field(
        default_factory=list,
        description="Services matching the query"
    )
    intents_found: List[IntentInfo] = Field(
        default_factory=list,
        description="Intents/capabilities found"
    )
    success: bool = Field(True, description="Whether the query was successful")
    error: Optional[str] = Field(None, description="Error message if query failed")
    mode: str = Field(..., description="Query mode used: 'keyword' or 'ai'")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Find me weather services",
                "response": "Found 2 weather services. Top matches: OpenWeather API, WeatherStack API.",
                "services_found": [
                    {
                        "id": "507f1f77bcf86cd799439011",
                        "name": "OpenWeather API",
                        "description": "Global weather data service",
                        "service_URL": "https://api.openweathermap.org",
                        "intent_ids": ["507f1f77bcf86cd799439012"]
                    }
                ],
                "intents_found": [
                    {
                        "id": "507f1f77bcf86cd799439012",
                        "name": "get_forecast",
                        "description": "Get weather forecast for a location",
                        "tags": ["weather", "forecast"],
                        "rateLimit": 1000,
                        "price": 0.0
                    }
                ],
                "success": True,
                "error": None,
                "mode": "keyword",
                "timestamp": "2025-12-04T10:30:00Z"
            }
        }
