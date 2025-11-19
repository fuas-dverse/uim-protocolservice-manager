# View data from the external mock web service
````bash
python agentClass.py --external http://localhost:4000 --action fetch-external
````

# Sync all fetched data into your local catalogue

````bash
python agentClass.py --external http://localhost:4000 --catalogue http://127.0.0.1:8000 --action sync
````

# View stored entries in your FastAPI service
````bash
python agentClass.py --catalogue http://127.0.0.1:8000 --action fetch-catalogue
````



to run the CLI use
````bash
python cli.py
````
