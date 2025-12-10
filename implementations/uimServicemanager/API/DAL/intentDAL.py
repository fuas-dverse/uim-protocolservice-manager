from bson import ObjectId
from typing import List, Optional, Dict, Any
from datetime import datetime
from .DBconnection import GetDBConnection
from pydantic import ValidationError
from logicLayer.validationModels.intentValidationModel import IntentDocument
from logicLayer.Interface.IintentDAL import IintentDAL

db = GetDBConnection()
intents_collection = db["intents"]


class IntentDAL(IintentDAL):

    def _document_to_dict(self, doc: dict) -> Optional[dict]:
        """Convert MongoDB document to dictionary with string ID"""
        if not doc:
            return None
        doc["id"] = str(doc.pop("_id"))
        return doc

    def getIntents(self) -> List[dict]:
        """Retrieve all intents from database"""
        intents_list = []
        for intent in intents_collection.find():
            intents_list.append(self._document_to_dict(intent))
        return intents_list

    def getIntentByID(self, intent_id: str) -> Optional[dict]:
        """Retrieve a single intent by ID"""
        if not ObjectId.is_valid(intent_id):
            return None

        intent = intents_collection.find_one({"_id": ObjectId(intent_id)})
        return self._document_to_dict(intent)

    def getIntentsByTag(self, tag: str) -> List[dict]:
        """Retrieve intents that contain the specified tag"""
        intents_list = []
        for intent in intents_collection.find({"tags": tag}):
            intents_list.append(self._document_to_dict(intent))
        return intents_list

    def addIntent(self, intent_data: Dict[str, Any]) -> str:
        """
        Add a new intent to the database using UIM-compliant format

        Args:
            intent_data: Dictionary with intent_uid, intent_name, http_method, etc.

        Returns:
            String ID of created intent
        """
        try:
            # Add timestamps
            intent_data["created_at"] = datetime.utcnow()
            intent_data["updated_at"] = datetime.utcnow()

            # Validate data using Pydantic model
            intent_doc = IntentDocument(**intent_data)

            # Insert into MongoDB
            result = intents_collection.insert_one(
                intent_doc.model_dump(by_alias=True, exclude={"id"})
            )
            return str(result.inserted_id)

        except ValidationError as e:
            raise ValueError(f"Validation error: {str(e)}")
        except Exception as e:
            raise Exception(f"Database error: {str(e)}")

    def updateIntent(self, intent_id: str, intent_data: Dict[str, Any]) -> bool:
        """
        Update an existing intent

        Args:
            intent_id: MongoDB ObjectId as string
            intent_data: Dictionary with fields to update

        Returns:
            True if successful, False otherwise
        """
        if not ObjectId.is_valid(intent_id):
            raise ValueError("Invalid intent ID format")

        try:
            # Update timestamp
            intent_data["updated_at"] = datetime.utcnow()

            # Remove any fields that shouldn't be updated
            intent_data.pop("id", None)
            intent_data.pop("_id", None)
            intent_data.pop("created_at", None)

            # Update in MongoDB
            result = intents_collection.update_one(
                {"_id": ObjectId(intent_id)},
                {"$set": intent_data}
            )

            return result.matched_count > 0

        except Exception as e:
            raise Exception(f"Database error: {str(e)}")

    def deleteIntent(self, intent_id: str) -> bool:
        """Delete an intent from the database"""
        if not ObjectId.is_valid(intent_id):
            raise ValueError("Invalid intent ID format")

        try:
            result = intents_collection.delete_one({"_id": ObjectId(intent_id)})
            return result.deleted_count > 0
        except Exception as e:
            raise Exception(f"Database error: {str(e)}")