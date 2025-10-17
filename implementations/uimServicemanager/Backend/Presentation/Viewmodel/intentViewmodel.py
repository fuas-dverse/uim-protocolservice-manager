from pydantic import BaseModel
from typing import Optional

class IntentViewModel(BaseModel):
    name: str
    description: str
    tags: str
    rateLimit: Optional[int] = None
    price: Optional[int] = None