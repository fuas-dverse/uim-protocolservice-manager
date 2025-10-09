from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["uim_database"]
users = db["users"]

users.insert_many([{"name": "Mike", "role": "Developer"},{"name": "John", "role": "Handyman"}])