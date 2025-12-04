from abc import ABC, abstractmethod

class IuimProtocol(ABC):
    @abstractmethod
    def getUIMProtocols(self):
        pass

    @abstractmethod
    def getProtocolByID(self, ID):
        pass

    @abstractmethod
    def adduimProtocol(self, uimpublickey, uimpolicyfile, uimApiDiscovery, uimApiExceute):
        pass

    @abstractmethod
    def updateProtocol(self, uimpublickey, uimpolicyfile, uimApiDiscovery, uimApiExceute, Protocol_id):
        pass

    @abstractmethod
    def deleteProtocol(self, Protocol_id):
        pass