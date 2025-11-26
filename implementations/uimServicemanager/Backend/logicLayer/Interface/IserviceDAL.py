from abc import ABC, abstractmethod
from typing import List, Optional


class IserviceDAL(ABC):

    @abstractmethod
    def getServices(self) -> List[dict]:
        """Retrieve all services"""
        pass

    @abstractmethod
    def getServiceByID(self, service_id: str) -> Optional[dict]:
        """Retrieve a service by ID"""
        pass

    @abstractmethod
    def addService(self, serviceName: str, serviceDescription: str,
                   service_URL: Optional[str]) -> str:
        """Add a new service and return its ID"""
        pass

    @abstractmethod
    def updateService(self, serviceName: str, serviceDescription: str,
                      service_URL: Optional[str], service_id: str) -> bool:
        """Update a service and return success status"""
        pass

    @abstractmethod
    def deleteService(self, service_id: str) -> bool:
        """Delete a service and return success status"""
        pass