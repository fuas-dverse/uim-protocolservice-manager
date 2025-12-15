"""
UIM Service Manager - Main API

Unified Intent Mediator service catalogue with REST and NATS interfaces.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from faststream.nats import NatsBroker
import os
import asyncio
from loguru import logger

from Presentation.Controller import servicesController
from Presentation.Controller import intentsController
from Presentation.Controller import uimProtocolController
from Presentation.Controller import queryController
from Presentation.Controller import discoveryController

nats_broker = None
nats_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    global nats_broker, nats_task

    # Startup
    logger.info("Starting UIM Service Manager...")

    nats_url = os.getenv("NATS_URL", "nats://localhost:4222")

    try:
        nats_broker = NatsBroker(nats_url)
        logger.info(f"Connecting to NATS at {nats_url}...")

        nats_task = asyncio.create_task(nats_broker.start())
        await asyncio.sleep(1)

        logger.info("NATS messaging initialized successfully")
        logger.info("   - Subscribed to: uim.catalogue.query")
        logger.info("   - Publishing to: uim.catalogue.response")

    except Exception as e:
        logger.warning(f"NATS connection failed: {e}")
        logger.warning("REST API will work, but NATS messaging is unavailable")
        nats_broker = None

    logger.info("UIM Service Manager started successfully")

    yield

    # Shutdown
    logger.info("Shutting down UIM Service Manager...")

    if nats_task:
        nats_task.cancel()
        try:
            await nats_task
        except asyncio.CancelledError:
            pass

    if nats_broker:
        await nats_broker.close()
        logger.info("NATS connection closed")

    logger.info("Shutdown complete")


app = FastAPI(
    title="UIM Service Manager",
    description="Unified Intent Mediator - Service Catalogue with Query Interface",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(servicesController.router, prefix="/services", tags=["Services"])
app.include_router(intentsController.router, prefix="/intents", tags=["Intents"])
app.include_router(uimProtocolController.router, prefix="/uimprotocol", tags=["UIM Protocol"])
app.include_router(queryController.router, prefix="/query", tags=["Query"])
app.include_router(discoveryController.router, prefix="/discovery", tags=["Discovery"])


@app.get("/")
def root():
    """Root endpoint with service information"""
    return {
        "message": "UIM Service Manager API",
        "version": "2.0.0",
        "status": "running",
        "features": {
            "rest_api": True,
            "nats_messaging": nats_broker is not None,
            "query_interface": True
        },
        "endpoints": {
            "services": "/services",
            "intents": "/intents",
            "uim_protocol": "/uimprotocol",
            "query": "/query",
            "documentation": "/docs"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "nats_connected": nats_broker is not None
    }


def get_nats_broker():
    """Dependency to get NATS broker instance"""
    return nats_broker