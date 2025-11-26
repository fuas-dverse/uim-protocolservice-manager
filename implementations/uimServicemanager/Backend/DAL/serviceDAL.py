from bson import ObjectId
from typing import List, Optional
from .DBconnection import GetDBConnection
from pydantic import ValidationError
from logicLayer.validationModels.serviceValidationModel import ServiceDocument
from logicLayer.Interface.IserviceDAL import IserviceDAL

db = GetDBConnection()
services_collection = db["services"]


class ServiceDAL(IserviceDAL):

    def _document_to_dict(self, doc: dict) -> Optional[dict]:
        """Convert MongoDB document to dictionary with string ID"""
        if not doc:
            return None
        doc["id"] = str(doc.pop("_id"))
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

    def addService(self, serviceName: str, serviceDescription: str, service_URL: Optional[str]) -> str:
        """Add a new service to the database"""
        try:
            data = {
                "name": serviceName,
                "description": serviceDescription,
                "service_URL": service_URL
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
                      service_URL: Optional[str], service_id: str) -> bool:
        """Update an existing service"""
        if not ObjectId.is_valid(service_id):
            raise ValueError("Invalid service ID format")

        try:
            data = {
                "name": serviceName,
                "description": serviceDescription,
                "service_URL": service_URL,
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