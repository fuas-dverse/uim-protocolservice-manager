from typing import List, Optional
from logicLayer.Interface.IintentDAL import IintentDAL
from Presentation.Viewmodel.intentViewmodel import IntentViewModel


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

    def addIntent(self, intentName: str, intentDescription: str,
                  intentTags: List[str], rateLimit: int, price: float) -> str:
        """Add a new intent and return the created ID"""
        return self.intentDAL.addIntent(intentName, intentDescription,
                                        intentTags, rateLimit, price)

    def updateIntent(self, intentName: str, intentDescription: str,
                     intentTags: List[str], rateLimit: int, price: float,
                     intent_id: str) -> bool:
        """Update an intent and return success status"""
        return self.intentDAL.updateIntent(intentName, intentDescription,
                                           intentTags, rateLimit, price, intent_id)

    def deleteIntent(self, intent_id: str) -> bool:
        """Delete an intent and return success status"""
        return self.intentDAL.deleteIntent(intent_id)