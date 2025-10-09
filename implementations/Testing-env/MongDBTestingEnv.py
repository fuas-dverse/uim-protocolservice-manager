from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["uim_database"]
users = db["users"]

print("All users")
for u in users.find():
    print(u)


print("All handymen")
developers = users.find({"role": "Handyman"})
for d in developers:
    print(d)
