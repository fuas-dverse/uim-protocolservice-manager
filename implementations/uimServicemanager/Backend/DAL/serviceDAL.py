from bson import ObjectId
from typing import List, Optional
from .DBconnection import GetDBConnection
from pydantic import ValidationError
from logicLayer.validationModels.serviceValidationModel import ServiceDocument
from logicLayer.validationModels.intentValidationModel import IntentDocument
from logicLayer.Interface.IserviceDAL import IserviceDAL

db = GetDBConnection()
services_collection = db["services"]
intents_collection = db["intents"]


class ServiceDAL(IserviceDAL):

    def _document_to_dict(self, doc: dict) -> Optional[dict]:
        """Convert MongoDB document to dictionary with string ID"""
        if not doc:
            return None
        doc["id"] = str(doc.pop("_id"))

        # Populate intents from intent_ids
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
        """Retrieve all services from database"""
        services_list = []
        for service in services_collection.find():
            services_list.append(self._document_to_dict(service))
        return services_list

    def getServiceByID(self, service_id: str) -> Optional[dict]:
        """Retrieve a single service by ID"""
        if not ObjectId.is_valid(service_id):
            return None

        service = services_collection.find_one({"_id": ObjectId(service_id)})
        return self._document_to_dict(service)

    def getServicesByName(self, name_query: str) -> List[dict]:
        """Search services by name using case-insensitive partial matching"""
        services_list = []
        # MongoDB regex for case-insensitive partial match
        regex_pattern = {"$regex": name_query, "$options": "i"}
        for service in services_collection.find({"name": regex_pattern}):
            services_list.append(self._document_to_dict(service))
        return services_list

    def addService(self, serviceName: str, serviceDescription: str,
                   service_URL: Optional[str], intent_ids: List[str]) -> str:
        """Add a new service to the database"""
        try:
            # Validate that all intent_ids exist
            for intent_id in intent_ids:
                if not ObjectId.is_valid(intent_id):
                    raise ValueError(f"Invalid intent ID format: {intent_id}")
                if not intents_collection.find_one({"_id": ObjectId(intent_id)}):
                    raise ValueError(f"Intent with ID {intent_id} does not exist")

            data = {
                "name": serviceName,
                "description": serviceDescription,
                "service_URL": service_URL,
                "intent_ids": intent_ids
            }
            # Validate data using Pydantic model
            service_doc = ServiceDocument(**data)

            # Insert into MongoDB
            result = services_collection.insert_one(
                service_doc.model_dump(by_alias=True, exclude={"id"})
            )
            return str(result.inserted_id)

        except ValidationError as e:
            raise ValueError(f"Validation error: {str(e)}")
        except Exception as e:
            raise Exception(f"Database error: {str(e)}")

    def updateService(self, serviceName: str, serviceDescription: str,
                      service_URL: Optional[str], intent_ids: List[str],
                      service_id: str) -> bool:
        """Update an existing service"""
        if not ObjectId.is_valid(service_id):
            raise ValueError("Invalid service ID format")

        try:
            # Validate that all intent_ids exist
            for intent_id in intent_ids:
                if not ObjectId.is_valid(intent_id):
                    raise ValueError(f"Invalid intent ID format: {intent_id}")
                if not intents_collection.find_one({"_id": ObjectId(intent_id)}):
                    raise ValueError(f"Intent with ID {intent_id} does not exist")

            data = {
                "name": serviceName,
                "description": serviceDescription,
                "service_URL": service_URL,
                "intent_ids": intent_ids
            }
            # Validate data using Pydantic model
            service_doc = ServiceDocument(**data)

            # Update in MongoDB (exclude _id from update)
            result = services_collection.update_one(
                {"_id": ObjectId(service_id)},
                {"$set": service_doc.model_dump(by_alias=True, exclude={"id"})}
            )

            return result.matched_count > 0

        except ValidationError as e:
            raise ValueError(f"Validation error: {str(e)}")
        except Exception as e:
            raise Exception(f"Database error: {str(e)}")

    def deleteService(self, service_id: str) -> bool:
        """Delete a service from the database"""
        if not ObjectId.is_valid(service_id):
            raise ValueError("Invalid service ID format")

        try:
            result = services_collection.delete_one({"_id": ObjectId(service_id)})
            return result.deleted_count > 0
        except Exception as e:
            raise Exception(f"Database error: {str(e)}")

    def addServiceWithIntents(self, serviceName: str, serviceDescription: str,
                              service_URL: Optional[str], intents_data: List[dict]) -> tuple[str, List[str]]:
        """Add a service and its intents in one transaction"""
        created_intent_ids = []

        try:
            # First, create all intents
            for intent_data in intents_data:
                # Validate and create intent
                intent_doc = IntentDocument(**intent_data)
                result = intents_collection.insert_one(
                    intent_doc.model_dump(by_alias=True, exclude={"id"})
                )
                created_intent_ids.append(str(result.inserted_id))

            # Then create the service with the intent IDs
            service_data = {
                "name": serviceName,
                "description": serviceDescription,
                "service_URL": service_URL,
                "intent_ids": created_intent_ids
            }
            service_doc = ServiceDocument(**service_data)

            result = services_collection.insert_one(
                service_doc.model_dump(by_alias=True, exclude={"id"})
            )
            service_id = str(result.inserted_id)

            return service_id, created_intent_ids

        except ValidationError as e:
            # Rollback: delete any intents that were created
            if created_intent_ids:
                for intent_id in created_intent_ids:
                    intents_collection.delete_one({"_id": ObjectId(intent_id)})
            raise ValueError(f"Validation error: {str(e)}")
        except Exception as e:
            # Rollback: delete any intents that were created
            if created_intent_ids:
                for intent_id in created_intent_ids:
                    intents_collection.delete_one({"_id": ObjectId(intent_id)})
            raise Exception(f"Database error: {str(e)}")