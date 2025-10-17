# Backend/Presentation/Controller/uimprotocolController.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List

from logicLayer.Logic.uimprotocolLogic import uimProtocolLogic
from DAL.uimprotocolDAL import uimProtocols
from Presentation.Viewmodel.uimProtocolViewmodel import uimProtocolViewModel  # your uimprotocol viewmodel

router = APIRouter()

# Dependency injection
def get_uimprotocol_logic():
    dal = uimProtocols()
    logic = uimProtocolLogic(dal)
    return logic

# GET all uimprotocol entries
@router.get("/", response_model=List[uimProtocolViewModel], description="Get all UIM Protocol entries")
def get_uimprotocols(logic: uimProtocolLogic = Depends(get_uimprotocol_logic)):
    protocols = logic.getUIMProtocols()
    return protocols

# GET by ID
@router.get("/{protocol_id}", response_model=uimProtocolViewModel, description="Get a UIM Protocol entry by ID")
def get_uimprotocol_by_id(protocol_id: str, logic: uimProtocolLogic = Depends(get_uimprotocol_logic)):
    protocol = logic.getUIMProtocolByID(protocol_id)
    if not protocol:
        raise HTTPException(status_code=404, detail="Protocol not found")
    return protocol

# POST a new entry
@router.post("/", response_model=dict, description="Create a UIM Protocol entry")
def create_uimprotocol(protocol: uimProtocolViewModel, logic: uimProtocolLogic = Depends(get_uimprotocol_logic)):
    result = logic.addUIMProtocol(protocol.uimpublickey, protocol.uimpolicyfile, protocol.uimApiDiscovery, protocol.uimApiExceute)
    return {"message": result}

# PUT update
@router.put("/{protocol_id}", response_model=dict, description="Update a UIM Protocol entry")
def update_uimprotocol(protocol_id: str, protocol: uimProtocolViewModel, logic: uimProtocolLogic = Depends(get_uimprotocol_logic)):
    result = logic.updateUIMProtocol(protocol.uimpublickey, protocol.uimpolicyfile, protocol.uimApiDiscovery, protocol.uimApiExceute, protocol_id)
    return {"message": result}

# DELETE
@router.delete("/{protocol_id}", response_model=dict, description="Delete a UIM Protocol entry")
def delete_uimprotocol(protocol_id: str, logic: uimProtocolLogic = Depends(get_uimprotocol_logic)):
    result = logic.deleteUIMProtocol(protocol_id)
    return {"message": result}
