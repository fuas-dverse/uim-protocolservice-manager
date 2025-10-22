import re
from fastapi import APIRouter, Depends, HTTPException
from typing import List

# Absolute imports
from logicLayer.Logic.serviceLogic import serviceLogic
from DAL.serviceDAL import ServiceDAL
from Presentation.Viewmodel.serviceViewmodel import ServiceViewModel



router = APIRouter()

# Dependency injection for service logic
def get_service_logic():
    dal = ServiceDAL()
    logic = serviceLogic(dal)
    return logic

# GET all services
@router.get("/", response_model=List[ServiceViewModel], description="Get all Services")
def get_services(logic: serviceLogic = Depends(get_service_logic)):
    services = logic.getServices()
    return services

# GET service by ID
@router.get("/{service_id}", response_model=ServiceViewModel, description="Get a Service by ID")
def get_service_by_id(service_id: str, logic: serviceLogic = Depends(get_service_logic)):
    service = logic.getServiceByID(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

# POST a new service
@router.post("/", response_model=dict, description="Create a Service", status_code=201)
def create_service(service: ServiceViewModel, logic: serviceLogic = Depends(get_service_logic)):
    regex = r"^[A-Za-z0-9 .]+$"
    if not re.match(regex, service.name):
        raise HTTPException(status_code=400, detail="Invalid name")
    if not re.match(regex, service.description):
        raise HTTPException(status_code=400, detail="Invalid description")

    result = logic.addService(service.name, service.description, service.service_URL)
    return {"message": result}

# PUT update service
@router.put("/{service_id}", response_model=dict, description="Update a Service")
def update_service(service_id: str, service: ServiceViewModel, logic: serviceLogic = Depends(get_service_logic)):
    regex = r"^[A-Za-z0-9 .]+$"
    if not re.match(regex, service.name):
        raise HTTPException(status_code=400, detail="Invalid name")
    if not re.match(regex, service.description):
        raise HTTPException(status_code=400, detail="Invalid description")

    result = logic.updateService(service.name, service.description, service.service_URL, service_id)
    return {"message": result}

# DELETE a service
@router.delete("/{service_id}", response_model=dict, description="Delete a Service")
def delete_service(service_id: str, logic: serviceLogic = Depends(get_service_logic)):
    result = logic.deleteService(service_id)
    return {"message": result}
