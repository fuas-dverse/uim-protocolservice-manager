"""
Discovery Viewmodels - Request/Response models for discovery endpoint

Defines the data structures for the LLM-based service discovery API.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional


class DiscoveryRequest(BaseModel):
    """Request model for service discovery"""
    user_query: str = Field(
        ...,
        min_length=3,
        description="Natural language query describing what the user wants to do",
        examples=[
            "Find papers about needle in a haystack problem",
            "What's the weather in Amsterdam?",
            "Create a GitHub repository",
            "Search for songs by The Beatles"
        ]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_query": "Find papers about AI and machine learning"
            }
        }


class DiscoveryResponse(BaseModel):
    """Response model for service discovery"""
    service: Dict[str, Any] = Field(
        ...,
        description="The complete service object with all intents and metadata"
    )
    selected_name: str = Field(
        ...,
        description="Name of the selected service"
    )
    reasoning: Optional[str] = Field(
        None,
        description="Explanation of why this service was selected"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "service": {
                    "id": "6937f343eb4165f5c391ff96",
                    "name": "arXiv API",
                    "description": "Access to scientific research papers...",
                    "service_url": "https://export.arxiv.org/api",
                    "intents": [
                        {
                            "id": "6937f343eb4165f5c391ff93",
                            "intent_name": "search_papers",
                            "description": "Search for research papers",
                            "tags": ["research", "papers", "academic", "search"]
                        }
                    ]
                },
                "selected_name": "arXiv API",
                "reasoning": "Selected based on query: 'Find papers about AI'"
            }
        }
