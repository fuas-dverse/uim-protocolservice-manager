import re
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from logicLayer.Logic.serviceLogic import ServiceLogic
from DAL.serviceDAL import ServiceDAL
from Presentation.Viewmodel.serviceViewmodel import (
    ServiceViewModel,
    ServiceCreateRequest,
    ServiceUpdateRequest,
    ServiceWithIntentsRequest
)

router = APIRouter()


# Dependency injection for service logic
def get_service_logic() -> ServiceLogic:
    dal = ServiceDAL()
    logic = ServiceLogic(dal)
    return logic


def validate_text_input(text: str, field_name: str) -> None:
    """Validate text input to prevent injection attacks"""
    regex = r"^[A-Za-z0-9 .,:;!?\-_()]+$"
    if not re.match(regex, text):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {field_name}: contains disallowed characters"
        )


# GET all services
@router.get(
    "/",
    response_model=List[ServiceViewModel],
    summary="Get all services",
    description="Retrieve a list of all registered services in the catalog"
)
def get_services(logic: ServiceLogic = Depends(get_service_logic)):
    try:
        return logic.getServices()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve services: {str(e)}"
        )


# GET service by ID
@router.get(
    "/{service_id}",
    response_model=ServiceViewModel,
    summary="Get service by ID",
    description="Retrieve a specific service by its unique identifier"
)
def get_service_by_id(
        service_id: str,
        logic: ServiceLogic = Depends(get_service_logic)
):
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


# POST a new service
@router.post(
    "/",
    response_model=dict,
    summary="Create a new service",
    description="Register a new service in the catalog",
    status_code=status.HTTP_201_CREATED
)
def create_service(
        service: ServiceCreateRequest,
        logic: ServiceLogic = Depends(get_service_logic)
):
    try:
        # Validate inputs
        validate_text_input(service.name, "name")
        validate_text_input(service.description, "description")

        # Create service
        service_id = logic.addService(
            service.name,
            service.description,
            service.service_URL,
            service.intent_ids
        )

        return {
            "message": "Service created successfully",
            "service_id": service_id
        }
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
            detail=f"Failed to create service: {str(e)}"
        )


# POST a new service with intents
@router.post(
    "/with-intents",
    response_model=dict,
    summary="Create a service with its intents",
    description="Register a new service and create its intents in a single request",
    status_code=status.HTTP_201_CREATED
)
def create_service_with_intents(
        request: ServiceWithIntentsRequest,
        logic: ServiceLogic = Depends(get_service_logic)
):
    try:
        # Validate service inputs
        validate_text_input(request.name, "name")
        validate_text_input(request.description, "description")

        # Validate each intent's text fields
        for idx, intent in enumerate(request.intents):
            if "name" in intent:
                validate_text_input(intent["name"], f"intent[{idx}].name")
            if "description" in intent:
                validate_text_input(intent["description"], f"intent[{idx}].description")
            if "tags" in intent and isinstance(intent["tags"], list):
                for tag in intent["tags"]:
                    validate_text_input(tag, f"intent[{idx}].tag")

        # Create service with intents
        service_id, intent_ids = logic.addServiceWithIntents(
            request.name,
            request.description,
            request.service_URL,
            request.intents
        )

        return {
            "message": "Service and intents created successfully",
            "service_id": service_id,
            "intent_ids": intent_ids
        }
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
            detail=f"Failed to create service with intents: {str(e)}"
        )


# PUT update service
@router.put(
    "/{service_id}",
    response_model=dict,
    summary="Update a service",
    description="Update an existing service's information"
)
def update_service(
        service_id: str,
        service: ServiceUpdateRequest,
        logic: ServiceLogic = Depends(get_service_logic)
):
    try:
        # Validate inputs
        validate_text_input(service.name, "name")
        validate_text_input(service.description, "description")

        # Update service
        success = logic.updateService(
            service.name,
            service.description,
            service.service_URL,
            service.intent_ids,
            service_id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service with ID '{service_id}' not found"
            )

        return {
            "message": "Service updated successfully",
            "service_id": service_id
        }
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


# DELETE a service
@router.delete(
    "/{service_id}",
    response_model=dict,
    summary="Delete a service",
    description="Remove a service from the catalog"
)
def delete_service(
        service_id: str,
        logic: ServiceLogic = Depends(get_service_logic)
):
    try:
        success = logic.deleteService(service_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service with ID '{service_id}' not found"
            )

        return {
            "message": "Service deleted successfully",
            "service_id": service_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete service: {str(e)}"
        )