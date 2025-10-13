from pymongo import MongoClient

def GetDBConnection():
    client = MongoClient('localhost', 27017)
    DB = client['service_protocol']
    return DB