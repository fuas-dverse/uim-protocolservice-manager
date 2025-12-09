from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017/")
db = client["servicemanager"]
db.services.delete_many({})
db.intents.delete_many({})
print("✅ Cleared all services and intents")