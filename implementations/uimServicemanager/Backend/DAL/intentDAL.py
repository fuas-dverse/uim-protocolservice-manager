from bson import ObjectId
from .DBconnection import GetDBConnection
from pydantic import ValidationError
from logicLayer.validationModels.intentModel import Intent
from logicLayer.Interface.IintentDAL import IintentDAL


db = GetDBConnection()
intents = db["intents"]

class IntentDAL(IintentDAL):
    def getIntents(self):
        IntentsList = []
        for intent in intents.find():
            IntentsList.append(intent)
        return IntentsList

    def getIntentByID(self ,ID):
        Intent = intents.find_one({"_id": ObjectId(ID)})
        return Intent

    def addIntents(self, intentName, intentDescription, intentTags, rateLimit, price):
        try:
            data = {
                "name": intentName,
                "description": intentDescription,
                "tags": intentTags,
                "rateLimit": rateLimit,
                "price": price
            }
            intent = Intent(**data)
            result = intents.insert_one(intent.model_dump(by_alias=True))
            return f"success: inserted with Id {result.inserted_id}"

        except ValidationError as e:
            return e

    def updateIntent(self, intentName, intentDescription, intentTags, rateLimit, price, Intents_ID):
        try:
            data = {
                "name": intentName,
                "description": intentDescription,
                "tags": intentTags,
                "rateLimit": rateLimit,
                "price": price,
            }
            intent = Intent(**data)
            result = intents.update_one({"_id": ObjectId(Intents_ID)}, {"$set": intent})
            return f"success: updated with Id {result.inserted_id}"
        except ValidationError as e:
            return e

    def deleteIntent(self, Intents_ID):
        try:
            intents.delete_one({"_id": ObjectId(Intents_ID)})
            return f"success: deleted with Id {Intents_ID}"
        except ValidationError as e:
            return e