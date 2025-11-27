from pydantic import BaseModel, Field
from typing import Optional, List
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom type for MongoDB ObjectId validation"""

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.union_schema([
            core_schema.is_instance_schema(ObjectId),
            core_schema.chain_schema([
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(cls.validate),
            ])
        ])

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")


class ServiceDocument(BaseModel):
    """MongoDB document model for services"""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    name: str = Field(..., min_length=2, max_length=50)
    description: str = Field(..., min_length=1, max_length=500)
    service_URL: Optional[str] = Field(None, max_length=500)
    intent_ids: List[str] = Field(default_factory=list, description="List of intent IDs")

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }