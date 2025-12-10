from bson import ObjectId
from typing import List, Optional
from datetime import datetime
from .DBconnection import GetDBConnection
from pydantic import ValidationError
from logicLayer.validationModels.serviceValidationModel import ServiceDocument
from logicLayer.validationModels.intentValidationModel import IntentDocument
from logicLayer.Interface.IserviceDAL import IserviceDAL

db = GetDBConnection()
services_collection = db["services"]
intents_collection = db["intents"]


class ServiceDAL(IserviceDAL):

    def _batch_populate_intents(self, services: List[dict]) -> List[dict]:
        """
        Populate intents for multiple services in ONE database query.

        This fixes the N+1 query problem where we were making
        individual queries for each intent.

        OLD: 1 service query + (N services × M intents) = 1 + (10 × 5) = 51 queries
        NEW: 1 service query + 1 intent query = 2 queries total
        """
        # Collect all unique intent IDs from all services
        all_intent_ids = set()
        for service in services:
            intent_ids = service.get("intent_ids", [])
            for intent_id in intent_ids:
                if ObjectId.is_valid(intent_id):
                    all_intent_ids.add(ObjectId(intent_id))

        # Fetch ALL intents in ONE query
        intent_docs = {}
        if all_intent_ids:
            intents_cursor = intents_collection.find({"_id": {"$in": list(all_intent_ids)}})
            for intent_doc in intents_cursor:
                intent_id_str = str(intent_doc["_id"])
                intent_doc["id"] = intent_id_str
                intent_doc.pop("_id")
                intent_docs[intent_id_str] = intent_doc

        # Now populate each service with its intents
        for service in services:
            service["id"] = str(service.pop("_id"))

            intent_ids = service.get("intent_ids", [])
            intents = []
            for intent_id in intent_ids:
                intent_id_str = str(intent_id)
                if intent_id_str in intent_docs:
                    intents.append(intent_docs[intent_id_str])

            service["intents"] = intents

        return services

    def _document_to_dict(self, doc: dict) -> Optional[dict]:
        """
        Convert single MongoDB document to dictionary with string ID.

        For single-document operations, still uses individual queries.
        For bulk operations, use _batch_populate_intents instead.
        """
        if not doc:
            return None
        doc["id"] = str(doc.pop("_id"))

        # Populate intents from intent_ids with FULL metadata
        intent_ids = doc.get("intent_ids", [])
        intents = []
        for intent_id in intent_ids:
            if ObjectId.is_valid(intent_id):
                intent_doc = intents_collection.find_one({"_id": ObjectId(intent_id)})
                if intent_doc:
                    intent_doc["id"] = str(intent_doc.pop("_id"))
                    intents.append(intent_doc)

        doc["intents"] = intents
        return doc


    def getServices(self) -> List[dict]:
        """
        Retrieve all services from database with full intent metadata.

        OPTIMIZED: Uses batch intent fetching instead of N+1 queries.
        """
        services = list(services_collection.find())
        return self._batch_populate_intents(services)

    def getServiceByID(self, service_id: str) -> Optional[dict]:
        """Retrieve a single service by ID with full intent metadata"""
        if not ObjectId.is_valid(service_id):
            return None

        service = services_collection.find_one({"_id": ObjectId(service_id)})
        return self._document_to_dict(service)

    def getServicesByName(self, name_query: str) -> List[dict]:
        """
        Search services by name using case-insensitive regex.
        Returns services with full intent metadata.

        OPTIMIZED: Uses batch intent fetching.
        """
        services = list(services_collection.find(
            {"name": {"$regex": name_query, "$options": "i"}}
        ))
        return self._batch_populate_intents(services)

    def addService(self, serviceName: str, serviceDescription: str,
                   service_URL: Optional[str], intent_ids: List[str]) -> str:
        """
        Add a new service (OLD interface method).

        Creates a minimal service with basic fields.
        For UIM-compliant services, use createService() instead.
        """
        service_data = {
            "name": serviceName,
            "description": serviceDescription,
            "service_url": service_URL,  # Use new field name
            "intent_ids": intent_ids,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        result = services_collection.insert_one(service_data)
        return str(result.inserted_id)

    def updateService(self, serviceName: str, serviceDescription: str,
                      service_URL: Optional[str], intent_ids: List[str],
                      service_id: str) -> bool:
        """Update a service (OLD interface method)"""
        if not ObjectId.is_valid(service_id):
            return False

        update_data = {
            "name": serviceName,
            "description": serviceDescription,
            "service_url": service_URL,  # Use new field name
            "intent_ids": intent_ids,
            "updated_at": datetime.utcnow()
        }

        result = services_collection.update_one(
            {"_id": ObjectId(service_id)},
            {"$set": update_data}
        )

        return result.modified_count > 0

    def deleteService(self, service_id: str) -> bool:
        """Delete a service"""
        if not ObjectId.is_valid(service_id):
            return False

        result = services_collection.delete_one({"_id": ObjectId(service_id)})
        return result.deleted_count > 0

    def addServiceWithIntents(self, serviceName: str, serviceDescription: str,
                              service_URL: Optional[str], intents_data: List[dict]) -> tuple[str, List[str]]:
        """Add a service and its intents together"""
        # First create all intents
        intent_ids = []
        for intent_data in intents_data:
            intent_result = intents_collection.insert_one(intent_data)
            intent_ids.append(str(intent_result.inserted_id))

        # Then create service with intent references
        service_id = self.addService(serviceName, serviceDescription, service_URL, intent_ids)

        return service_id, intent_ids


    def createService(self, service_data: dict) -> dict:
        """
        Create a new UIM-compliant service with full metadata.

        Note: Intents should be created first, then their IDs passed here.
        """
        # Validate with Pydantic
        try:
            validated_service = ServiceDocument(**service_data)
        except ValidationError as e:
            raise ValueError(f"Service validation failed: {e}")

        # Convert to dict for MongoDB
        service_dict = validated_service.model_dump(by_alias=True)

        # Insert into database
        result = services_collection.insert_one(service_dict)

        # Return the created service with populated intents
        return self.getServiceByID(str(result.inserted_id))

    def updateServiceNew(self, service_id: str, service_data: dict) -> Optional[dict]:
        """
        Update an existing UIM-compliant service with full metadata.

        This is the new method that handles auth_type, etc.
        """
        if not ObjectId.is_valid(service_id):
            return None

        # Validate with Pydantic (partial update allowed)
        try:
            validated_service = ServiceDocument(**service_data)
        except ValidationError as e:
            raise ValueError(f"Service validation failed: {e}")

        # Convert to dict
        service_dict = validated_service.model_dump(by_alias=True, exclude_unset=True)

        # Update timestamp
        service_dict["updated_at"] = datetime.utcnow()

        # Update in database
        result = services_collection.update_one(
            {"_id": ObjectId(service_id)},
            {"$set": service_dict}
        )

        if result.modified_count > 0:
            return self.getServiceByID(service_id)
        return None

    def getServiceWithIntents(self, service_id: str) -> Optional[dict]:
        """
        Get service with fully populated intent metadata.

        This is useful for the chatbot to get ALL info needed for invocation.
        """
        return self.getServiceByID(service_id)

    def searchServicesByTags(self, tags: List[str]) -> List[dict]:
        """
        Search services by intent tags.

        OPTIMIZED: Uses batch intent fetching.
        """
        # Find intents with matching tags
        matching_intents = list(intents_collection.find(
            {"tags": {"$in": tags}}
        ))

        # Get intent IDs
        intent_ids = [str(intent["_id"]) for intent in matching_intents]

        # Find services containing these intents
        services = list(services_collection.find(
            {"intent_ids": {"$in": intent_ids}}
        ))

        return self._batch_populate_intents(services)