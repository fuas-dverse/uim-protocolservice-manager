from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class IserviceDAL(ABC):

    # ==================== OLD Interface Methods (Required for Backwards Compatibility) ====================

    @abstractmethod
    def getServices(self) -> List[dict]:
        """Retrieve all services"""
        pass

    @abstractmethod
    def getServiceByID(self, service_id: str) -> Optional[dict]:
        """Retrieve a service by ID"""
        pass

    @abstractmethod
    def getServicesByName(self, name_query: str) -> List[dict]:
        """Search services by name (partial match, case-insensitive)"""
        pass

    @abstractmethod
    def addService(self, serviceName: str, serviceDescription: str,
                   service_URL: Optional[str], intent_ids: List[str]) -> str:
        """Add a new service and return its ID"""
        pass

    @abstractmethod
    def updateService(self, serviceName: str, serviceDescription: str,
                      service_URL: Optional[str], intent_ids: List[str],
                      service_id: str) -> bool:
        """Update a service and return success status"""
        pass

    @abstractmethod
    def deleteService(self, service_id: str) -> bool:
        """Delete a service and return success status"""
        pass

    @abstractmethod
    def addServiceWithIntents(self, serviceName: str, serviceDescription: str,
                              service_URL: Optional[str], intents_data: List[dict]) -> tuple[str, List[str]]:
        """Add a service and its intents in one transaction. Returns (service_id, list of intent_ids)"""
        pass

    # ==================== NEW UIM-Compliant Methods ====================

    @abstractmethod
    def createService(self, service_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new UIM-compliant service with full metadata.

        Args:
            service_data: Service data matching ServiceDocument structure

        Returns:
            Created service with full metadata (including populated intents)
        """
        pass

    @abstractmethod
    def updateServiceNew(self, service_id: str, service_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update an existing UIM-compliant service.

        Args:
            service_id: Service ID to update
            service_data: Partial service data to update

        Returns:
            Updated service with full metadata or None if not found
        """
        pass

    @abstractmethod
    def searchServicesByTags(self, tags: List[str]) -> List[Dict[str, Any]]:
        """
        Search services by intent tags.

        Args:
            tags: List of tags to search for

        Returns:
            List of services whose intents match any of the tags
        """
        pass

    @abstractmethod
    def getServiceWithIntents(self, service_id: str) -> Optional[Dict[str, Any]]:
        """
        Get service with fully populated intent metadata.

        Args:
            service_id: Service ID

        Returns:
            Service with intents array fully populated with metadata
        """
        pass