"""
Main FastAPI application for HubSpot Deals ETL Service
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from api.routes import extraction, health
from config.settings import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting HubSpot Deals ETL Service...")
    yield
    logger.info("Shutting down HubSpot Deals ETL Service...")


app = FastAPI(
    title="HubSpot Deals ETL Service",
    description="ETL service for extracting HubSpot deals data using DLT",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(extraction.router, prefix="/api/v1", tags=["Extraction"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "HubSpot Deals ETL",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/docs")
async def docs_redirect():
    """Redirect to API documentation"""
    return {"docs_url": "/docs"}

