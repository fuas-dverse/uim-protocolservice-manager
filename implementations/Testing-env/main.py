from Mongo_connection import GetDBConnection
from models import User
from pydantic import ValidationError

db = GetDBConnection()
users = db.users
nameint = "test"

data = {
    "name": nameint,
    "age": 22
}

try:
    user = User(**data)
    print("Validated User:", user.model_dump())

    result = users.insert_one(user.model_dump(by_alias=True, exclude_none=True))
    print("Inserted with ID:", result.inserted_id)

except ValidationError as e:
    print("validation failed:", e )