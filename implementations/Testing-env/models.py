from pydantic import BaseModel, Field, EmailStr
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


class User(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    name: str = Field(..., min_length=2, max_length=50)
    age: int = Field(..., gt=2, lt=50)

    class Config:
        json_encoders = {ObjectId: str}
        validate_by_name = True
        arbitrary_types_allowed = True