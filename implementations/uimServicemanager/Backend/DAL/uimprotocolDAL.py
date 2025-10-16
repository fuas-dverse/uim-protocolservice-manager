from bson import ObjectId
from DBconnection import GetDBConnection
from pydantic import ValidationError
from implementations.uimServicemanager.Backend.Logic.validationModels.UIMprotocolModel import Protocol
from implementations.uimServicemanager.Backend.Logic.Interface.IuimprotocolDAL import IuimProtocol

db = GetDBConnection()
uimProtocols = db["UIMprotocol"]

class ProtocolDAL(IuimProtocol):
    def getUIMProtocols(self):
        uimprotocolLists = []
        for uimprotocolList in uimProtocols.find():
            uimprotocolLists.append(uimprotocolList)
        return uimprotocolLists

    def getProtocolByID(self, ID):
        uimProtocol = uimProtocols.find_one({"_id": ObjectId(ID)})
        return uimProtocol

    def adduimProtocol(self, uimpublickey, uimpolicyfile, uimApiDiscovery, uimApiExceute):
        try:
            data = {
                "uimpublickey": uimpublickey,
                "uimpolicyfile": uimpolicyfile,
                "uimApiDiscovery": uimApiDiscovery,
                "uimApiExceute": uimApiExceute
            }
            uimProtocol = Protocol(**data)
            result = uimProtocols.insert_one(uimProtocol.model_dump(by_alias=True))
            return f"success: inserted with Id {result.inserted_id}"

        except ValidationError as e:
            return e

    def updateProtocol(self, uimpublickey, uimpolicyfile, uimApiDiscovery, uimApiExceute, Protocol_id):
        try:
            data = {
                "uimpublickey": uimpublickey,
                "uimpolicyfile": uimpolicyfile,
                "uimApiDiscovery": uimApiDiscovery,
                "uimApiExceute": uimApiExceute
            }
            intent = Protocol(**data)
            result = uimProtocols.update_one({"_id": ObjectId(Protocol_id)}, {"$set": intent})
            return f"success: updated with Id {result.inserted_id}"
        except ValidationError as e:
            return e

    def deleteProtocol(self, Protocol_id):
        try:
            uimProtocols.delete_one({"_id": ObjectId(Protocol_id)})
            return f"success: deleted with Id {Protocol_id}"
        except ValidationError as e:
            return e