"""
Services Controller - Updated for UIM-compliant services

Handles CRUD operations for services with full metadata.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional

from logicLayer.Logic.serviceLogic import ServiceLogic
from DAL.serviceDAL import ServiceDAL
from Presentation.Viewmodel.serviceViewmodel import (
    ServiceCreateRequest,
    ServiceUpdateRequest,
    ServiceResponse,
    ServiceListResponse
)

router = APIRouter()


def get_service_logic() -> ServiceLogic:
    """Dependency injection for service logic"""
    service_dal = ServiceDAL()
    return ServiceLogic(service_dal)


@router.get(
    "/",
    response_model=ServiceListResponse,
    summary="Get all services",
    description="Retrieve all services with full intent metadata"
)
def get_all_services(
    logic: ServiceLogic = Depends(get_service_logic),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)")
):
    """Get all services, optionally filtered by tags"""
    try:
        if tags:
            tag_list = [t.strip() for t in tags.split(",")]
            services = logic.searchServicesByTags(tag_list)
        else:
            services = logic.getAllServices()

        return ServiceListResponse(
            services=services,
            total=len(services)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve services: {str(e)}"
        )


@router.get(
    "/{service_id}",
    response_model=ServiceResponse,
    summary="Get service by ID",
    description="Retrieve a specific service with full intent metadata"
)
def get_service(
    service_id: str,
    logic: ServiceLogic = Depends(get_service_logic)
):
    """Get a specific service by ID"""
    try:
        service = logic.getServiceByID(service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service with ID '{service_id}' not found"
            )
        return service
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve service: {str(e)}"
        )


@router.post(
    "/",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new service",
    description="""
    Create a new service with UIM-compliant structure.
    
    Note: Intents must be created first, then reference their IDs here.
    """
)
def create_service(
    service: ServiceCreateRequest,
    logic: ServiceLogic = Depends(get_service_logic)
):
    """Create a new service"""
    try:
        created_service = logic.createService(service.model_dump())
        return created_service
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create service: {str(e)}"
        )


@router.put(
    "/{service_id}",
    response_model=ServiceResponse,
    summary="Update a service",
    description="Update an existing service (partial updates allowed)"
)
def update_service(
    service_id: str,
    service: ServiceUpdateRequest,
    logic: ServiceLogic = Depends(get_service_logic)
):
    """Update an existing service"""
    try:
        # Only include fields that were actually provided
        update_data = service.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update"
            )

        updated_service = logic.updateServiceNew(service_id, update_data)

        if not updated_service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service with ID '{service_id}' not found"
            )

        return updated_service
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update service: {str(e)}"
        )


@router.delete(
    "/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a service",
    description="Delete a service (intents are NOT deleted)"
)
def delete_service(
    service_id: str,
    logic: ServiceLogic = Depends(get_service_logic)
):
    """Delete a service"""
    try:
        success = logic.deleteService(service_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service with ID '{service_id}' not found"
            )

        return None  # 204 No Content
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete service: {str(e)}"
        )


@router.get(
    "/search/by-name",
    response_model=ServiceListResponse,
    summary="Search services by name",
    description="Search for services using case-insensitive name matching"
)
def search_services_by_name(
    query: str = Query(..., min_length=1, description="Search query"),
    logic: ServiceLogic = Depends(get_service_logic)
):
    """Search services by name"""
    try:
        services = logic.searchServicesByName(query)
        return ServiceListResponse(
            services=services,
            total=len(services)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search services: {str(e)}"
        )