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
                   service_URL: Optional[str]) -> str:
        """Add a new service and return the created ID"""
        return self.serviceDAL.addService(serviceName, serviceDescription, service_URL)

    def updateService(self, serviceName: str, serviceDescription: str,
                      service_URL: Optional[str], service_id: str) -> bool:
        """Update a service and return success status"""
        return self.serviceDAL.updateService(serviceName, serviceDescription,
                                             service_URL, service_id)

    def deleteService(self, service_id: str) -> bool:
        """Delete a service and return success status"""
        return self.serviceDAL.deleteService(service_id)