from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Presentation.Controller import servicesController
from Presentation.Controller import intentsController
from Presentation.Controller import uimProtocolController

app = FastAPI(title="UIMservicemanager")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],)

# include routes
app.include_router(servicesController.router, prefix="/services", tags=["Services"])
app.include_router(intentsController.router, prefix="/intents", tags=["Intents"])
app.include_router(uimProtocolController.router, prefix="/uimprotocol", tags=["UIMprotocol"])

@app.get("/")
def root():
    return {"message": "FastAPI is running!"}
