from abc import ABC, abstractmethod

class IintentDAL(ABC):
    @abstractmethod
    def getIntents(self):
        pass
    @abstractmethod
    def getIntentByID(self, ID):
        pass
    @abstractmethod
    def getIntentByTag(self, Tag):
        pass
    @abstractmethod
    def addIntent(self, intentName, intentDescription, intentTags, rateLimit, price):
        pass
    @abstractmethod
    def updateIntent(self, intentName, intentDescription, intentTags, rateLimit, price, Intents_ID):
        pass

    @abstractmethod
    def deleteIntent(self, Intents_ID):
        pass