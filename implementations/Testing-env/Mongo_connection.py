from pymongo import MongoClient

def GetDBConnection():
    client = MongoClient('localhost', 27017)
    DB = client['Testing_Pydantic_DB']
    return DB