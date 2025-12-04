from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

class IntentViewModel(BaseModel):
    """View model for intent responses"""
    id: Optional[str] = Field(None, description="Intent ID (auto-generated)")
    name: str = Field(..., min_length=2, max_length=50)
    description: str = Field(..., min_length=1, max_length=500)
    tags: List[str] = Field(default_factory=list)
    rateLimit: int = Field(..., ge=0, description="Rate limit (requests per time period)")
    price: float = Field(..., ge=0, description="Price for using this intent")

    @field_validator("rateLimit", mode="before")
    @classmethod
    def parse_rate_limit(cls, v):
        if v is None:
            return 0
        return int(v)

    @field_validator("price", mode="before")
    @classmethod
    def parse_price(cls, v):
        if v is None:
            return 0.0
        return float(v)


class IntentCreateRequest(BaseModel):
    """Request model for creating an intent"""
    name: str = Field(..., min_length=2, max_length=50)
    description: str = Field(..., min_length=1, max_length=500)
    tags: List[str] = Field(default_factory=list)
    rateLimit: int = Field(..., ge=0, description="Rate limit (requests per time period)")
    price: float = Field(..., ge=0, description="Price for using this intent")

    @field_validator("rateLimit", mode="before")
    @classmethod
    def parse_rate_limit(cls, v):
        if v is None:
            return 0
        return int(v)

    @field_validator("price", mode="before")
    @classmethod
    def parse_price(cls, v):
        if v is None:
            return 0.0
        return float(v)


class IntentUpdateRequest(BaseModel):
    """Request model for updating an intent"""
    name: str = Field(..., min_length=2, max_length=50)
    description: str = Field(..., min_length=1, max_length=500)
    tags: List[str] = Field(default_factory=list)
    rateLimit: int = Field(..., ge=0, description="Rate limit (requests per time period)")
    price: float = Field(..., ge=0, description="Price for using this intent")

    @field_validator("rateLimit", mode="before")
    @classmethod
    def parse_rate_limit(cls, v):
        if v is None:
            return 0
        return int(v)

    @field_validator("price", mode="before")
    @classmethod
    def parse_price(cls, v):
        if v is None:
            return 0.0
        return float(v)