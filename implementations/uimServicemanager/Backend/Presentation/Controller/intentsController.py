# Backend/Presentation/Controller/intentsController.py
import re
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional

from logicLayer.Logic.intentLogic import intentLogic
from DAL.intentDAL import IntentDAL
from Presentation.Viewmodel.intentViewmodel import IntentViewModel
router = APIRouter()

# Dependency injection
def get_intents_logic():
    dal = IntentDAL()
    logic = intentLogic(dal)
    return logic

# GET all intents
@router.get("/", response_model=List[IntentViewModel], description="Get all Intents")
def get_intents(logic: intentLogic = Depends(get_intents_logic)):
    intents = logic.getIntents()
    return intents

# GET intent by ID
@router.get("/{intent_id}", response_model=IntentViewModel, description="Get an Intent by ID")
def get_intent_by_id(intent_id: str, logic: intentLogic = Depends(get_intents_logic)):
    intent = logic.getIntentByID(intent_id)
    if not intent:
        raise HTTPException(status_code=404, detail="Intent not found")
    return intent

# GET intent by Tag
@router.get("/{intent_tag}", response_model=IntentViewModel, description="Get an Intent by tag")
def get_intent_by_tag(intent_tag: str, logic: intentLogic = Depends(get_intents_logic)):
    intent = logic.getIntentByTag(intent_tag)
    if not intent:
        raise HTTPException(status_code=404, detail="Intent not found")
    return intent

# POST a new intent
@router.post("/", response_model=dict, description="Create an Intent", status_code=201)
def create_intent(intent: IntentViewModel, logic: intentLogic = Depends(get_intents_logic)):
    regex = r"^[A-Za-z0-9 .]+$"
    if not re.match(regex, intent.name):
        raise HTTPException(status_code=400, detail="Invalid name")
    if not re.match(regex, intent.description):
        raise HTTPException(status_code=400, detail="Invalid description")

    result = logic.addIntent(intent.name, intent.description, intent.tags, intent.rateLimit, intent.price)
    return {"message": result}

# PUT update intent
@router.put("/{intent_id}", response_model=dict, description="Update an Intent")
def update_intent(intent_id: str, intent: IntentViewModel, logic: intentLogic = Depends(get_intents_logic)):
    regex = r"^[A-Za-z0-9 .]+$"
    if not re.match(regex, intent.name):
        raise HTTPException(status_code=400, detail="Invalid name")
    if not re.match(regex, intent.description):
        raise HTTPException(status_code=400, detail="Invalid description")

    result = logic.updateIntent(intent.name, intent.description, intent.tags, intent.rateLimit, intent.price, intent_id)
    return {"message": result}

# DELETE an intent
@router.delete("/{intent_id}", response_model=dict, description="Delete an Intent")
def delete_intent(intent_id: str, logic: intentLogic = Depends(get_intents_logic)):
    result = logic.deleteIntent(intent_id)
    return {"message": result}
