"""
US Market Hours Calendar - FastAPI Backend
Main application entry point
"""
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.routers import market_hours, docs
from app.scheduler import start_scheduler, shutdown_scheduler
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    logger.info("Starting US Market Hours Calendar API")
    
    # Start scheduler on startup
    start_scheduler()
    logger.info("Scheduler started")
    
    yield
    
    # Cleanup on shutdown
    shutdown_scheduler()
    logger.info("Scheduler stopped")


# Initialize FastAPI app
app = FastAPI(
    title="US Market Hours Calendar API",
    description="Real-time US stock market hours and holiday schedules",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None,  # Disable default docs
    redoc_url=None  # Disable default redoc
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    market_hours.router,
    prefix="/market-hours",
    tags=["market-hours"]
)

app.include_router(
    docs.router,
    prefix="/documentation",
    tags=["documentation"]
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "US Market Hours Calendar API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

