from pydantic import BaseModel, Field
from typing import Optional

class ServiceViewModel(BaseModel):
    """View model for service responses and requests"""
    id: Optional[str] = Field(None, description="Service ID (auto-generated)")
    name: str = Field(..., min_length=2, max_length=50)
    description: str = Field(..., min_length=1, max_length=500)
    service_URL: Optional[str] = Field(None, max_length=500)

class ServiceCreateRequest(BaseModel):
    """Request model for creating a service"""
    name: str = Field(..., min_length=2, max_length=50)
    description: str = Field(..., min_length=1, max_length=500)
    service_URL: Optional[str] = Field(None, max_length=500)

class ServiceUpdateRequest(BaseModel):
    """Request model for updating a service"""
    name: str = Field(..., min_length=2, max_length=50)
    description: str = Field(..., min_length=1, max_length=500)
    service_URL: Optional[str] = Field(None, max_length=500)