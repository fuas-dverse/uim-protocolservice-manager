first run this command for the Database to run in one terminal based in UIM-protocol

.\implementations\uimServicemanager\Backend\DAL\mongoDB-Configs\bin\mongod.exe --dbpath "..\data" --logpath "..\log\mongod.log" --port 27017

or in this command if your within the config/bin

.\mongod.exe --dbpath "..\data" --logpath "..\log\mongod.log" --port 27017



then run the program (run this command within the backend main folder)

python -m uvicorn main:app --reload

the port it uses is:  http://127.0.0.1:8000


alternative you can also run within the backend folder:
python StartupService.py
