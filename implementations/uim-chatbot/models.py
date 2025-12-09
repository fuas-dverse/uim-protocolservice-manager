"""
Pydantic models for chatbot messages (Pydantic v2 compatible).

These define the structure of messages exchanged between users and the chatbot.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime


class ChatbotQuery(BaseModel):
    """
    Message sent by users to the chatbot.

    POST /chat endpoint
    """
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "user_id": "user-123",
            "message": "Find recent papers about multi-agent systems",
            "context": {},
            "timestamp": "2025-12-08T10:00:00Z"
        }
    })

    user_id: str = Field(..., description="Unique identifier for the user")
    message: str = Field(..., description="User's message/question")
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional context (conversation history, preferences, etc.)"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ServiceInvocationResult(BaseModel):
    """Result from invoking an external service"""
    service_name: str
    intent_name: str
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ChatbotResponse(BaseModel):
    """
    Message sent back to users with chatbot's response.

    Returned from POST /chat endpoint
    """
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "user_id": "user-123",
            "message": "I found 5 recent papers about multi-agent systems...",
            "query": "Find recent papers about multi-agent systems",
            "services_discovered": ["arXiv API"],
            "service_invocation": {
                "service_name": "arXiv API",
                "intent_name": "search_papers",
                "success": True,
                "data": {"papers": []}
            },
            "success": True,
            "error": None,
            "timestamp": "2025-12-08T10:00:01Z"
        }
    })

    user_id: str = Field(..., description="User this response is for")
    message: str = Field(..., description="Chatbot's natural language response")
    query: str = Field(..., description="Original user query")
    services_discovered: List[str] = Field(
        default_factory=list,
        description="Names of services discovered"
    )
    service_invocation: Optional[ServiceInvocationResult] = Field(
        None,
        description="Result of invoking the external service"
    )
    success: bool = Field(True, description="Whether the query was successful")
    error: Optional[str] = Field(None, description="Error message if query failed")
    timestamp: datetime = Field(default_factory=datetime.utcnow)