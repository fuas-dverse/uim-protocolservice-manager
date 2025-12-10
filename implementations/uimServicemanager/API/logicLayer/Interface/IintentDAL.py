from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


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
    def addIntent(self, intent_data: Dict[str, Any]) -> str:
        """
        Add a new intent and return its ID

        Args:
            intent_data: Dictionary with intent_uid, intent_name, http_method, etc.

        Returns:
            String ID of created intent
        """
        pass

    @abstractmethod
    def updateIntent(self, intent_id: str, intent_data: Dict[str, Any]) -> bool:
        """
        Update an intent and return success status

        Args:
            intent_id: MongoDB ObjectId as string
            intent_data: Dictionary with fields to update

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def deleteIntent(self, intent_id: str) -> bool:
        """Delete an intent and return success status"""
        pass