from pydantic import BaseModel, Field
from typing import Optional, List

class ServiceViewModel(BaseModel):
    """View model for service responses and requests"""
    id: Optional[str] = Field(None, description="Service ID (auto-generated)")
    name: str = Field(..., min_length=2, max_length=50)
    description: str = Field(..., min_length=1, max_length=500)
    service_URL: Optional[str] = Field(None, max_length=500)
    intents: List[dict] = Field(default_factory=list, description="List of associated intents")

class ServiceCreateRequest(BaseModel):
    """Request model for creating a service"""
    name: str = Field(..., min_length=2, max_length=50)
    description: str = Field(..., min_length=1, max_length=500)
    service_URL: Optional[str] = Field(None, max_length=500)
    intent_ids: List[str] = Field(default_factory=list, description="List of intent IDs to associate")

class ServiceUpdateRequest(BaseModel):
    """Request model for updating a service"""
    name: str = Field(..., min_length=2, max_length=50)
    description: str = Field(..., min_length=1, max_length=500)
    service_URL: Optional[str] = Field(None, max_length=500)
    intent_ids: List[str] = Field(default_factory=list, description="List of intent IDs to associate")

class ServiceWithIntentsRequest(BaseModel):
    """Request model for creating a service with its intents in one call"""
    name: str = Field(..., min_length=2, max_length=50)
    description: str = Field(..., min_length=1, max_length=500)
    service_URL: Optional[str] = Field(None, max_length=500)
    intents: List[dict] = Field(..., description="List of intent objects to create")