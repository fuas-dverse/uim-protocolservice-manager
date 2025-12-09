"""
Service Logic - Updated for UIM-compliant services

Handles both old-style methods (for backwards compatibility)
and new UIM-compliant methods.
"""
from typing import List, Optional, Dict, Any
from logicLayer.Interface.IserviceDAL import IserviceDAL
from Presentation.Viewmodel.serviceViewmodel import (
    ServiceResponse,
    ServiceCreateRequest,
    ServiceUpdateRequest
)


class ServiceLogic:
    """Business logic layer for service operations"""

    def __init__(self, serviceDAL: IserviceDAL):
        self.serviceDAL = serviceDAL

    # ==================== OLD Methods (Backwards Compatibility) ====================

    def getServices(self) -> List[Dict[str, Any]]:
        """
        Get all services (OLD method).

        Returns raw dicts for compatibility.
        """
        return self.serviceDAL.getServices()

    def getServiceByID(self, service_id: str) -> Optional[Dict[str, Any]]:
        """Get a single service by ID (returns dict)"""
        return self.serviceDAL.getServiceByID(service_id)

    def getServicesByName(self, name_query: str) -> List[Dict[str, Any]]:
        """Search services by name (returns dicts)"""
        return self.serviceDAL.getServicesByName(name_query)

    def addService(self, serviceName: str, serviceDescription: str,
                   service_URL: Optional[str], intent_ids: List[str]) -> str:
        """Add a new service (OLD method) and return the created ID"""
        return self.serviceDAL.addService(serviceName, serviceDescription,
                                          service_URL, intent_ids)

    def updateService(self, serviceName: str, serviceDescription: str,
                      service_URL: Optional[str], intent_ids: List[str],
                      service_id: str) -> bool:
        """Update a service (OLD method) and return success status"""
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

    # ==================== NEW UIM-Compliant Methods ====================

    def getAllServices(self) -> List[Dict[str, Any]]:
        """
        Get all services with full UIM metadata.

        Used by new controller methods.
        """
        return self.serviceDAL.getServices()

    def searchServicesByName(self, name_query: str) -> List[Dict[str, Any]]:
        """
        Search services by name with full metadata.

        Used by new controller methods.
        """
        return self.serviceDAL.getServicesByName(name_query)

    def searchServicesByTags(self, tags: List[str]) -> List[Dict[str, Any]]:
        """
        Search services by intent tags.

        Used by new controller methods.
        """
        return self.serviceDAL.searchServicesByTags(tags)

    def createService(self, service_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new UIM-compliant service.

        Args:
            service_data: Dict matching ServiceCreateRequest structure

        Returns:
            Created service with full metadata
        """
        return self.serviceDAL.createService(service_data)

    def updateServiceNew(self, service_id: str, service_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a UIM-compliant service.

        Args:
            service_id: Service ID to update
            service_data: Dict with fields to update

        Returns:
            Updated service or None if not found
        """
        return self.serviceDAL.updateServiceNew(service_id, service_data)