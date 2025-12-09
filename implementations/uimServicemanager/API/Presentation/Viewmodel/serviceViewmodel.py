"""
Service Viewmodel - Updated for UIM-compliant structure

Used for HTTP request/response validation in controllers.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime


class ParameterSchemaView(BaseModel):
    """View model for intent parameter schema"""
    name: str
    type: Literal["string", "integer", "number", "boolean", "array", "object"]
    description: Optional[str] = None
    required: bool = True
    default: Optional[Any] = None
    location: Literal["query", "path", "body", "header"] = "body"


class IntentView(BaseModel):
    """View model for intent (used in service responses)"""
    id: Optional[str] = Field(None, description="Intent ID (auto-generated)")
    intent_uid: str
    intent_name: str
    description: Optional[str] = None
    http_method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"] = "POST"
    endpoint_path: str
    input_parameters: List[Dict[str, Any]] = Field(default_factory=list)
    output_schema: Optional[Dict[str, Any]] = None
    tags: List[str] = Field(default_factory=list)
    rateLimit: Optional[int] = None
    price: float = 0.0


class ServiceCreateRequest(BaseModel):
    """Request model for creating a new service"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "OpenWeather API",
            "description": "Weather data and forecasts",
            "service_url": "https://api.openweathermap.org/data/2.5",
            "auth_type": "api_key",
            "auth_query_param": "appid",
            "intent_ids": ["intent_id_1", "intent_id_2"]
        }
    })

    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)

    # Service URLs
    service_url: str = Field(..., description="Base URL for API calls")
    service_logo_url: Optional[str] = None
    service_terms_url: Optional[str] = None
    service_privacy_url: Optional[str] = None

    # Authentication
    auth_type: Optional[Literal["none", "api_key", "oauth", "bearer"]] = "none"
    auth_header_name: Optional[str] = None
    auth_query_param: Optional[str] = None

    # Intents (as list of IDs)
    intent_ids: List[str] = Field(default_factory=list, description="List of intent IDs to associate")

    # UIM Protocol fields
    uim_api_discovery: Optional[str] = None
    uim_api_execute: Optional[str] = None


class ServiceUpdateRequest(BaseModel):
    """Request model for updating a service (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    service_url: Optional[str] = None
    service_logo_url: Optional[str] = None
    service_terms_url: Optional[str] = None
    service_privacy_url: Optional[str] = None
    auth_type: Optional[Literal["none", "api_key", "oauth", "bearer"]] = None
    auth_header_name: Optional[str] = None
    auth_query_param: Optional[str] = None
    intent_ids: Optional[List[str]] = None
    uim_api_discovery: Optional[str] = None
    uim_api_execute: Optional[str] = None


class ServiceResponse(BaseModel):
    """Response model for service (returned from GET/POST/PUT)"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "507f1f77bcf86cd799439011",
            "name": "OpenWeather API",
            "description": "Weather data and forecasts",
            "service_url": "https://api.openweathermap.org/data/2.5",
            "auth_type": "api_key",
            "auth_query_param": "appid",
            "intent_ids": ["intent_id_1"],
            "intents": [{
                "id": "intent_id_1",
                "intent_uid": "openweather:getCurrentWeather:v1",
                "intent_name": "get_current_weather",
                "http_method": "GET",
                "endpoint_path": "/weather",
                "tags": ["weather", "current"]
            }],
            "created_at": "2024-12-08T12:00:00Z",
            "updated_at": "2024-12-08T12:00:00Z"
        }
    })
    id: str
    name: str
    description: Optional[str] = None

    # Service URLs
    service_url: str
    service_logo_url: Optional[str] = None
    service_terms_url: Optional[str] = None
    service_privacy_url: Optional[str] = None

    # Authentication
    auth_type: Optional[str] = "none"
    auth_header_name: Optional[str] = None
    auth_query_param: Optional[str] = None

    # Intents (populated with full metadata)
    intent_ids: List[str] = Field(default_factory=list)
    intents: List[IntentView] = Field(default_factory=list, description="Full intent metadata")

    # UIM Protocol fields
    uim_api_discovery: Optional[str] = None
    uim_api_execute: Optional[str] = None

    # Timestamps
    created_at: datetime
    updated_at: datetime


class ServiceListResponse(BaseModel):
    """Response model for listing services"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "services": [],
            "total": 10
        }
    })

    services: List[ServiceResponse]
    total: int