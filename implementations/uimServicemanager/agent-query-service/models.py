"""
Pydantic models for NATS messages.

These define the structure of messages exchanged between agents and the AQS.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class QueryMessage(BaseModel):
    """
    Message sent by agents to query the UIM catalogue.
    
    Published to: uim.catalogue.query
    """
    agent_id: str = Field(..., description="Unique identifier for the requesting agent")
    message: str = Field(..., description="Natural language query from the agent")
    context: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Optional context information (e.g., previous queries, agent state)"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "agent-weather-001",
                "message": "Find me weather services that support forecasting",
                "context": {"location": "Europe", "previous_service": "openweather"},
                "timestamp": "2025-12-02T10:30:00Z"
            }
        }


class ServiceInfo(BaseModel):
    """Information about a service from the catalogue"""
    id: str
    name: str
    description: Optional[str] = None
    base_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class IntentInfo(BaseModel):
    """Information about an intent/capability of a service"""
    id: str
    name: str
    description: Optional[str] = None
    service_id: str
    parameters: Dict[str, Any] = Field(default_factory=dict)


class ResponseMessage(BaseModel):
    """
    Message sent back to agents with query results.
    
    Published to: uim.catalogue.response
    """
    agent_id: str = Field(..., description="Agent this response is for")
    query: str = Field(..., description="Original query from the agent")
    response: str = Field(..., description="Natural language response")
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
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "agent-weather-001",
                "query": "Find me weather services",
                "response": "I found 2 weather services with forecasting capabilities.",
                "services_found": [
                    {
                        "id": "service-123",
                        "name": "OpenWeather API",
                        "description": "Global weather data service"
                    }
                ],
                "intents_found": [
                    {
                        "id": "intent-456",
                        "name": "get_forecast",
                        "description": "Get weather forecast for a location",
                        "service_id": "service-123"
                    }
                ],
                "success": True,
                "error": None,
                "timestamp": "2025-12-02T10:30:01Z"
            }
        }
