from pydantic import BaseModel
from typing import Optional

class ServiceViewModel(BaseModel):
    name: str
    description: str
    service_URL: Optional[str] = None
