# View data from the external mock web service
python agent.py --external http://localhost:4000 --action fetch-external

# Sync all fetched data into your local catalogue
python agent.py --external http://localhost:4000 --catalogue http://127.0.0.1:8000 --action sync

# View stored entries in your FastAPI service
python agent.py --catalogue http://127.0.0.1:8000 --action fetch-catalogue
