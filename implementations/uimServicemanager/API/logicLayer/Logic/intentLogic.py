from typing import List, Optional
from logicLayer.Interface.IintentDAL import IintentDAL
from Presentation.Viewmodel.intentViewmodel import IntentViewModel, IntentCreateRequest, IntentUpdateRequest


class IntentLogic:
    """Business logic layer for intent operations"""

    def __init__(self, intentDAL: IintentDAL):
        self.intentDAL = intentDAL

    def getIntents(self) -> List[IntentViewModel]:
        """Get all intents"""
        intents_data = self.intentDAL.getIntents()
        return [IntentViewModel(**intent) for intent in intents_data]

    def getIntentByID(self, intent_id: str) -> Optional[IntentViewModel]:
        """Get a single intent by ID"""
        intent_data = self.intentDAL.getIntentByID(intent_id)
        if intent_data:
            return IntentViewModel(**intent_data)
        return None

    def getIntentsByTag(self, tag: str) -> List[IntentViewModel]:
        """Get intents by tag"""
        intents_data = self.intentDAL.getIntentsByTag(tag)
        return [IntentViewModel(**intent) for intent in intents_data]

    def addIntent(self, intent_request: IntentCreateRequest) -> str:
        """
        Add a new intent and return the created ID

        Args:
            intent_request: IntentCreateRequest with UIM-compliant fields

        Returns:
            String ID of created intent
        """
        # Convert Pydantic model to dict
        intent_data = intent_request.model_dump(exclude_none=True)
        return self.intentDAL.addIntent(intent_data)

    def updateIntent(self, intent_id: str, intent_request: IntentUpdateRequest) -> bool:
        """
        Update an intent and return success status

        Args:
            intent_id: MongoDB ObjectId as string
            intent_request: IntentUpdateRequest with fields to update

        Returns:
            True if successful, False otherwise
        """
        # Convert Pydantic model to dict, exclude None values
        intent_data = intent_request.model_dump(exclude_none=True)

        # Only update if there are fields to update
        if not intent_data:
            return False

        return self.intentDAL.updateIntent(intent_id, intent_data)

    def deleteIntent(self, intent_id: str) -> bool:
        """Delete an intent and return success status"""
        return self.intentDAL.deleteIntent(intent_id)