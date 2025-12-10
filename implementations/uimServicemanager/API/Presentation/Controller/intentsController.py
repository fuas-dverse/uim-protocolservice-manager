import re
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List

from logicLayer.Logic.intentLogic import IntentLogic
from DAL.intentDAL import IntentDAL
from Presentation.Viewmodel.intentViewmodel import (
    IntentViewModel,
    IntentCreateRequest,
    IntentUpdateRequest
)

router = APIRouter()


# Dependency injection
def get_intents_logic() -> IntentLogic:
    dal = IntentDAL()
    logic = IntentLogic(dal)
    return logic


def validate_text_input(text: str, field_name: str) -> None:
    """Validate text input to prevent injection attacks"""
    # Allow more characters for UIM format (colons for intent_uid, underscores for intent_name)
    regex = r"^[A-Za-z0-9 .,:;!?\-_()/@]+$"
    if not re.match(regex, text):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {field_name}: contains disallowed characters"
        )


# GET all intents OR filter by tag using query parameter
@router.get(
    "/",
    response_model=List[IntentViewModel],
    summary="Get all intents or filter by tag",
    description="Retrieve all intents or filter by tag using ?tag=tagname query parameter"
)
def get_intents(
        tag: str = Query(None, description="Filter intents by tag"),
        logic: IntentLogic = Depends(get_intents_logic)
):
    try:
        if tag:
            # Filter by tag if provided
            return logic.getIntentsByTag(tag)
        else:
            # Return all intents
            return logic.getIntents()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve intents: {str(e)}"
        )


# GET intent by ID
@router.get(
    "/{intent_id}",
    response_model=IntentViewModel,
    summary="Get intent by ID",
    description="Retrieve a specific intent by its unique identifier"
)
def get_intent_by_id(
        intent_id: str,
        logic: IntentLogic = Depends(get_intents_logic)
):
    try:
        intent = logic.getIntentByID(intent_id)
        if not intent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Intent with ID '{intent_id}' not found"
            )
        return intent
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve intent: {str(e)}"
        )


# POST a new intent
@router.post(
    "/",
    response_model=dict,
    summary="Create a new intent",
    description="Register a new intent in the catalog with UIM-compliant structure",
    status_code=status.HTTP_201_CREATED
)
def create_intent(
        intent: IntentCreateRequest,
        logic: IntentLogic = Depends(get_intents_logic)
):
    try:
        # Validate inputs
        validate_text_input(intent.intent_uid, "intent_uid")
        validate_text_input(intent.intent_name, "intent_name")
        if intent.description:
            validate_text_input(intent.description, "description")

        # Validate tags
        for tag in intent.tags:
            validate_text_input(tag, "tag")

        # Create intent
        intent_id = logic.addIntent(intent)

        return {
            "message": "Intent created successfully",
            "intent_id": intent_id
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
            detail=f"Failed to create intent: {str(e)}"
        )


# POST bulk intents
@router.post(
    "/bulk",
    response_model=dict,
    summary="Create multiple intents",
    description="Register multiple intents in the catalog at once",
    status_code=status.HTTP_201_CREATED
)
def create_bulk_intents(
        intents: List[IntentCreateRequest],
        logic: IntentLogic = Depends(get_intents_logic)
):
    try:
        created_ids = []
        errors = []

        for idx, intent in enumerate(intents):
            try:
                # Validate inputs
                validate_text_input(intent.intent_uid, "intent_uid")
                validate_text_input(intent.intent_name, "intent_name")
                if intent.description:
                    validate_text_input(intent.description, "description")

                for tag in intent.tags:
                    validate_text_input(tag, "tag")

                # Create intent
                intent_id = logic.addIntent(intent)
                created_ids.append(intent_id)

            except Exception as e:
                errors.append({
                    "index": idx,
                    "intent_name": intent.intent_name,
                    "error": str(e)
                })

        return {
            "message": f"Created {len(created_ids)} intent(s)",
            "created_ids": created_ids,
            "errors": errors if errors else None
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create bulk intents: {str(e)}"
        )


# PUT update intent
@router.put(
    "/{intent_id}",
    response_model=dict,
    summary="Update an intent",
    description="Update an existing intent's information"
)
def update_intent(
        intent_id: str,
        intent: IntentUpdateRequest,
        logic: IntentLogic = Depends(get_intents_logic)
):
    try:
        # Validate inputs if provided
        if intent.intent_uid:
            validate_text_input(intent.intent_uid, "intent_uid")
        if intent.intent_name:
            validate_text_input(intent.intent_name, "intent_name")
        if intent.description:
            validate_text_input(intent.description, "description")

        if intent.tags:
            for tag in intent.tags:
                validate_text_input(tag, "tag")

        # Update intent
        success = logic.updateIntent(intent_id, intent)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Intent with ID '{intent_id}' not found"
            )

        return {"message": "Intent updated successfully"}

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
            detail=f"Failed to update intent: {str(e)}"
        )


# DELETE intent
@router.delete(
    "/{intent_id}",
    response_model=dict,
    summary="Delete an intent",
    description="Remove an intent from the catalog"
)
def delete_intent(
        intent_id: str,
        logic: IntentLogic = Depends(get_intents_logic)
):
    try:
        success = logic.deleteIntent(intent_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Intent with ID '{intent_id}' not found"
            )

        return {"message": "Intent deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete intent: {str(e)}"
        )