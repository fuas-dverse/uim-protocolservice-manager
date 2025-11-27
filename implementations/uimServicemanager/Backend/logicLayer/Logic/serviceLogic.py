from typing import List, Optional
from logicLayer.Interface.IserviceDAL import IserviceDAL
from Presentation.Viewmodel.serviceViewmodel import ServiceViewModel


class ServiceLogic:
    """Business logic layer for service operations"""

    def __init__(self, serviceDAL: IserviceDAL):
        self.serviceDAL = serviceDAL

    def getServices(self) -> List[ServiceViewModel]:
        """Get all services"""
        services_data = self.serviceDAL.getServices()
        return [ServiceViewModel(**service) for service in services_data]

    def getServiceByID(self, service_id: str) -> Optional[ServiceViewModel]:
        """Get a single service by ID"""
        service_data = self.serviceDAL.getServiceByID(service_id)
        if service_data:
            return ServiceViewModel(**service_data)
        return None

    def addService(self, serviceName: str, serviceDescription: str,
                   service_URL: Optional[str], intent_ids: List[str]) -> str:
        """Add a new service and return the created ID"""
        return self.serviceDAL.addService(serviceName, serviceDescription,
                                          service_URL, intent_ids)

    def updateService(self, serviceName: str, serviceDescription: str,
                      service_URL: Optional[str], intent_ids: List[str],
                      service_id: str) -> bool:
        """Update a service and return success status"""
        return self.serviceDAL.updateService(serviceName, serviceDescription,
                                             service_URL, intent_ids, service_id)

    def deleteService(self, service_id: str) -> bool:
        """Delete a service and return success status"""
        return self.serviceDAL.deleteService(service_id)

    def addServiceWithIntents(self, serviceName: str, serviceDescription: str,
                              service_URL: Optional[str], intents_data: List[dict]) -> tuple[str, List[str]]:
        """Add a service with its intents in one call"""
        return self.serviceDAL.addServiceWithIntents(serviceName, serviceDescription,
                                                     service_URL, intents_data)