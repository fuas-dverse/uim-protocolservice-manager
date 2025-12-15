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

        all_intent_ids = set()
        for service in services:
            intent_ids = service.get("intent_ids", [])
            for intent_id in intent_ids:
                if ObjectId.is_valid(intent_id):
                    all_intent_ids.add(ObjectId(intent_id))


        intent_docs = {}
        if all_intent_ids:
            intents_cursor = intents_collection.find({"_id": {"$in": list(all_intent_ids)}})
            for intent_doc in intents_cursor:
                intent_id_str = str(intent_doc["_id"])
                intent_doc["id"] = intent_id_str
                intent_doc.pop("_id")
                intent_docs[intent_id_str] = intent_doc


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

        if not doc:
            return None
        doc["id"] = str(doc.pop("_id"))


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
        services = list(services_collection.find())
        return self._batch_populate_intents(services)

    def getServiceByID(self, service_id: str) -> Optional[dict]:
        """Retrieve a single service by ID with full intent metadata"""
        if not ObjectId.is_valid(service_id):
            return None

        service = services_collection.find_one({"_id": ObjectId(service_id)})
        return self._document_to_dict(service)

    def getServicesByName(self, name_query: str) -> List[dict]:

        services = list(services_collection.find(
            {"name": {"$regex": name_query, "$options": "i"}}
        ))
        return self._batch_populate_intents(services)

    def addService(self, serviceName: str, serviceDescription: str,
                   service_URL: Optional[str], intent_ids: List[str]) -> str:

        service_data = {
            "name": serviceName,
            "description": serviceDescription,
            "service_url": service_URL,
            "intent_ids": intent_ids,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        result = services_collection.insert_one(service_data)
        return str(result.inserted_id)

    def updateService(self, serviceName: str, serviceDescription: str,
                      service_URL: Optional[str], intent_ids: List[str],
                      service_id: str) -> bool:

        if not ObjectId.is_valid(service_id):
            return False

        update_data = {
            "name": serviceName,
            "description": serviceDescription,
            "service_url": service_URL,
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
        """
        try:
            validated_service = ServiceDocument(**service_data)
        except ValidationError as e:
            raise ValueError(f"Service validation failed: {e}")


        service_dict = validated_service.model_dump(by_alias=True)


        result = services_collection.insert_one(service_dict)


        return self.getServiceByID(str(result.inserted_id))

    def updateServiceNew(self, service_id: str, service_data: dict) -> Optional[dict]:
        """
        Update an existing UIM-compliant service with full metadata.
        """
        if not ObjectId.is_valid(service_id):
            return None


        try:
            validated_service = ServiceDocument(**service_data)
        except ValidationError as e:
            raise ValueError(f"Service validation failed: {e}")


        service_dict = validated_service.model_dump(by_alias=True, exclude_unset=True)


        service_dict["updated_at"] = datetime.utcnow()


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
        """

        matching_intents = list(intents_collection.find(
            {"tags": {"$in": tags}}
        ))


        intent_ids = [str(intent["_id"]) for intent in matching_intents]

        
        services = list(services_collection.find(
            {"intent_ids": {"$in": intent_ids}}
        ))

        return self._batch_populate_intents(services)