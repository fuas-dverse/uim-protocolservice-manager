from bson import ObjectId
from .DBconnection import GetDBConnection
from pydantic import ValidationError
from logicLayer.validationModels.serviceModel import Service
from logicLayer.Interface.IserviceDAL import IserviceDAL


db = GetDBConnection()
services = db["services"]

class ServiceDAL(IserviceDAL):
    def getServices(self):
        ServicesList = []
        for service in services.find():
            ServicesList.append(service)
        return ServicesList

    def getServiceByID(self, ID):
        service = services.find_one({"_id": ObjectId(ID)})
        return service

    def addService(self, serviceName, serviceDescription, service_URL):
        try:
            data = {
                "name": serviceName,
                "description": serviceDescription,
                "service_URL": service_URL
            }
            service = Service(**data)
            result = services.insert_one(service.model_dump(by_alias=True))
            return f"success: inserted with Id {result.inserted_id}"

        except ValidationError as e:
            return e

    def updateService(self, serviceName, serviceDescription, service_URL, Service_ID):
        try:
            data = {
                "name": serviceName,
                "description": serviceDescription,
                "service_URL": service_URL,
            }
            service = Service(**data)
            result = services.update_one({"_id": ObjectId(Service_ID)}, {"$set": service})
            return f"success: updated with Id {result.inserted_id}"
        except ValidationError as e:
            return e

    def deleteService(self, Service_ID):
        try:
            services.delete_one({"_id": ObjectId(Service_ID)})
            return f"success: deleted with Id {Service_ID}"
        except ValidationError as e:
            return e





