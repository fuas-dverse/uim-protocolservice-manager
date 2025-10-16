from implementations.uimServicemanager.Backend.Logic.Interface.IuimprotocolDAL import IuimProtocol

class uimProtocolLogic:
    def __init__(self, protocolDal: IuimProtocol):
        self.protocolDal = protocolDal

    def getUIMProtocols(self):
        return self.protocolDal.getUIMProtocols()

    def getProtocolByID(self, ID):
        return self.protocolDal.getProtocolByID(ID)

    def adduimProtocol(self, uimpublickey, uimpolicyfile, uimApiDiscovery, uimApiExceute):
        return self.protocolDal.adduimProtocol(uimpublickey, uimpolicyfile, uimApiDiscovery, uimApiExceute)

    def updateProtocol(self, uimpublickey, uimApiDiscovery, uimApiExceute, Protocol_id):
        return self.protocolDal.updateProtocol(uimpublickey, uimApiDiscovery, uimApiExceute, Protocol_id)

    def deleteProtocol(self, Protocol_id):
        return self.protocolDal.deleteProtocol(Protocol_id)