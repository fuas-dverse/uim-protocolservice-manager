from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional, Dict, Any, Literal


class IntentViewModel(BaseModel):
    """
    View model for intent responses - UIM-compliant format

    This matches the actual database structure after the merge.
    """
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "507f1f77bcf86cd799439011",
            "intent_uid": "openweather:getCurrentWeather:v1",
            "intent_name": "get_current_weather",
            "description": "Get current weather for a city",
            "http_method": "GET",
            "endpoint_path": "/weather",
            "input_parameters": [
                {
                    "name": "q",
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

    id: Optional[str] = Field(None, description="Intent ID (auto-generated)")
    intent_uid: str = Field(..., description="Unique identifier (format: service:intent:version)")
    intent_name: str = Field(..., description="Human-readable intent name")
    description: Optional[str] = Field(None, description="What this intent does")

    # API Invocation Details
    http_method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"] = Field("POST", description="HTTP method to use")
    endpoint_path: str = Field(..., description="Path to append to service_url")

    # Parameters
    input_parameters: List[Dict[str, Any]] = Field(default_factory=list, description="Input parameters schema")
    output_schema: Optional[Dict[str, Any]] = Field(None, description="Expected response schema")

    # Metadata
    tags: List[str] = Field(default_factory=list, description="Searchable tags")
    rateLimit: Optional[int] = Field(None, description="Rate limit (requests per minute)")
    price: float = Field(0.0, description="Cost per request")


class IntentCreateRequest(BaseModel):
    """Request model for creating an intent - UIM-compliant"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "intent_uid": "myservice:myIntent:v1",
            "intent_name": "my_intent",
            "description": "Does something useful",
            "http_method": "POST",
            "endpoint_path": "/api/action",
            "input_parameters": [],
            "tags": ["utility"],
            "rateLimit": 100,
            "price": 0.0
        }
    })

    intent_uid: str = Field(..., description="Unique identifier (format: service:intent:version)")
    intent_name: str = Field(..., min_length=2, max_length=100, description="Human-readable intent name")
    description: Optional[str] = Field(None, max_length=500, description="What this intent does")

    # API Invocation Details
    http_method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"] = Field("POST", description="HTTP method")
    endpoint_path: str = Field(..., description="Path to append to service_url")

    # Parameters
    input_parameters: List[Dict[str, Any]] = Field(default_factory=list, description="Input parameters schema")
    output_schema: Optional[Dict[str, Any]] = Field(None, description="Expected response schema")

    # Metadata
    tags: List[str] = Field(default_factory=list, description="Searchable tags")
    rateLimit: Optional[int] = Field(None, ge=0, description="Rate limit (requests per minute)")
    price: float = Field(0.0, ge=0, description="Cost per request")

    @field_validator("rateLimit", mode="before")
    @classmethod
    def parse_rate_limit(cls, v):
        if v is None:
            return None
        return int(v)

    @field_validator("price", mode="before")
    @classmethod
    def parse_price(cls, v):
        if v is None:
            return 0.0
        return float(v)


class IntentUpdateRequest(BaseModel):
    """Request model for updating an intent - all fields optional"""
    intent_uid: Optional[str] = Field(None, description="Unique identifier")
    intent_name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

    http_method: Optional[Literal["GET", "POST", "PUT", "DELETE", "PATCH"]] = None
    endpoint_path: Optional[str] = None

    input_parameters: Optional[List[Dict[str, Any]]] = None
    output_schema: Optional[Dict[str, Any]] = None

    tags: Optional[List[str]] = None
    rateLimit: Optional[int] = Field(None, ge=0)
    price: Optional[float] = Field(None, ge=0)

    @field_validator("rateLimit", mode="before")
    @classmethod
    def parse_rate_limit(cls, v):
        if v is None:
            return None
        return int(v)

    @field_validator("price", mode="before")
    @classmethod
    def parse_price(cls, v):
        if v is None:
            return None
        return float(v)