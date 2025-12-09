"""
Intent Validation Model - UIM Protocol Compliant (Pydantic v2)

Stored separately from services for flexibility.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime


class IntentDocument(BaseModel):
    """
    Intent document for MongoDB storage.

    Matches IntentMetadata from serviceValidationModel but stored as separate document.
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
                    "name": "q",
                    "type": "string",
                    "description": "City name",
                    "required": True,
                    "location": "query"
                },
                {
                    "name": "units",
                    "type": "string",
                    "description": "Temperature units (metric/imperial)",
                    "required": False,
                    "default": "metric",
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
    endpoint_path: str = Field(..., description="Path to append to service_url")

    # Parameters - stored as list of dicts for MongoDB
    input_parameters: List[Dict[str, Any]] = Field(default_factory=list, description="Input parameters schema")
    output_schema: Optional[Dict[str, Any]] = Field(None, description="Expected response schema")

    # Metadata
    tags: List[str] = Field(default_factory=list, description="Searchable tags")
    rateLimit: Optional[int] = Field(None, description="Rate limit (requests per minute)")
    price: float = Field(0.0, description="Cost per request")

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)