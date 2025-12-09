"""
Service Validation Model - UIM Protocol Compliant (Pydantic v2)

This model extends the basic service structure to include:
- API endpoint information for generic invocation
- HTTP method and parameter mapping
- Input/output schemas (Pydantic models)
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime


class ParameterSchema(BaseModel):
    """Schema for intent parameters"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "city",
            "type": "string",
            "description": "City name for weather lookup",
            "required": True,
            "location": "query"
        }
    })

    name: str = Field(..., description="Parameter name")
    type: Literal["string", "integer", "number", "boolean", "array", "object"] = Field(..., description="Parameter type")
    description: Optional[str] = Field(None, description="Parameter description")
    required: bool = Field(True, description="Whether parameter is required")
    default: Optional[Any] = Field(None, description="Default value if not provided")
    location: Literal["query", "path", "body", "header"] = Field("body", description="Where parameter goes in HTTP request")


class IntentMetadata(BaseModel):
    """
    Intent metadata including API invocation details.

    This allows generic service invocation without hardcoding each API.
    """
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "intent_uid": "openweather.com:getCurrentWeather:v1",
            "intent_name": "get_current_weather",
            "description": "Get current weather for a city",
            "http_method": "GET",
            "endpoint_path": "/weather",
            "input_parameters": [
                {
                    "name": "city",
                    "type": "string",
                    "description": "City name",
                    "required": True,
                    "location": "query"
                }
            ],
            "tags": ["weather", "current"],
            "rateLimit": 60,
            "price": 0.0
        }
    })

    intent_uid: str = Field(..., description="Unique identifier (format: service:intent:version)")
    intent_name: str = Field(..., description="Human-readable intent name")
    description: Optional[str] = Field(None, description="What this intent does")

    # API Invocation Details
    http_method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"] = Field("POST", description="HTTP method to use")
    endpoint_path: str = Field(..., description="Path to append to service_url (e.g., '/weather')")

    # Parameters
    input_parameters: List[ParameterSchema] = Field(default_factory=list, description="Input parameters schema")
    output_schema: Optional[Dict[str, Any]] = Field(None, description="Expected response schema (JSON Schema)")

    # Metadata
    tags: List[str] = Field(default_factory=list, description="Searchable tags")
    rateLimit: Optional[int] = Field(None, description="Rate limit (requests per minute)")
    price: float = Field(0.0, description="Cost per request")


class ServiceDocument(BaseModel):
    """
    Service document for MongoDB storage - UIM Protocol compliant.

    Includes all metadata needed for generic service invocation.
    """
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "OpenWeather API",
            "description": "Weather data and forecasts for any location worldwide",
            "service_url": "https://api.openweathermap.org/data/2.5",
            "auth_type": "api_key",
            "auth_query_param": "appid",
            "intent_ids": ["intent_id_1", "intent_id_2"]
        }
    })

    name: str = Field(..., description="Service name")
    description: Optional[str] = Field(None, description="Service description")

    # Service URLs
    service_url: str = Field(..., description="Base URL for API calls")
    service_logo_url: Optional[str] = Field(None, description="Logo URL")
    service_terms_url: Optional[str] = Field(None, description="Terms of service URL")
    service_privacy_url: Optional[str] = Field(None, description="Privacy policy URL")

    # Authentication (for future use)
    auth_type: Optional[Literal["none", "api_key", "oauth", "bearer"]] = Field("none", description="Authentication type")
    auth_header_name: Optional[str] = Field(None, description="Header name for auth (e.g., 'X-API-Key')")
    auth_query_param: Optional[str] = Field(None, description="Query param for auth (e.g., 'api_key')")

    # Intents with full metadata
    intent_ids: List[str] = Field(default_factory=list, description="List of intent IDs (populated from IntentMetadata)")

    # UIM Protocol fields
    uim_api_discovery: Optional[str] = Field(None, description="Endpoint for intent discovery")
    uim_api_execute: Optional[str] = Field(None, description="Standard UIM execution endpoint (if available)")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)