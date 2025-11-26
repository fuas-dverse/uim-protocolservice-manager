from abc import ABC, abstractmethod
from typing import List, Optional


class IintentDAL(ABC):

    @abstractmethod
    def getIntents(self) -> List[dict]:
        """Retrieve all intents"""
        pass

    @abstractmethod
    def getIntentByID(self, intent_id: str) -> Optional[dict]:
        """Retrieve an intent by ID"""
        pass

    @abstractmethod
    def getIntentsByTag(self, tag: str) -> List[dict]:
        """Retrieve intents by tag"""
        pass

    @abstractmethod
    def addIntent(self, intentName: str, intentDescription: str,
                  intentTags: List[str], rateLimit: int, price: float) -> str:
        """Add a new intent and return its ID"""
        pass

    @abstractmethod
    def updateIntent(self, intentName: str, intentDescription: str,
                     intentTags: List[str], rateLimit: int, price: float,
                     intent_id: str) -> bool:
        """Update an intent and return success status"""
        pass

    @abstractmethod
    def deleteIntent(self, intent_id: str) -> bool:
        """Delete an intent and return success status"""
        pass