from pydantic import BaseModel, field_validator, Field
from typing import List, Optional

class IntentViewModel(BaseModel):
    intent_name: str = Field(alias="name")
    description: str
    tags: List[str]
    rateLimit: Optional[int] = None
    price: Optional[float] = None

    class Config:
        extra = "allow"

    @field_validator("rateLimit", mode="before")
    def parse_rate_limit(cls, v):
        if v is None:
            return None
        return int(v)

    @field_validator("price", mode="before")
    def parse_price(cls, v):
        if v is None:
            return None
        return float(v)
