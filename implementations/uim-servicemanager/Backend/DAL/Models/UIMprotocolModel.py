from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)


class Protocol(BaseModel):
    Protocol_id: Optional[PyObjectId] = Field(default=None, alias="_id")
    uimpublickey: str = Field(..., min_length=1, max_length=500)
    uimpolicyfile: str = Field(..., min_length=1, max_length=500)
    uimApiDiscovery: str = Field(..., min_length=1, max_length=500)
    uimApiExceute: str = Field(..., min_length=1, max_length=500)


    class Config:
        json_encoders = {ObjectId: str}
        validate_by_name = True
        arbitrary_types_allowed = True