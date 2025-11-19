"""
Vectal.ai Clone - FastAPI Backend
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import logging

from api.routes import health
from utils.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Vectal.ai Clone API",
    description="AI-powered productivity platform with task management, chat, and more",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip Middleware for response compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])

# Import routes
from api.routes import auth, oauth, tasks, projects, notes
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(oauth.router, prefix="/api/v1/oauth", tags=["OAuth"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["Tasks"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["Projects"])
app.include_router(notes.router, prefix="/api/v1/notes", tags=["Notes"])

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An internal server error occurred",
                "details": str(exc) if settings.DEBUG else None
            }
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting Vectal.ai Clone API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Initialize database connections
    from db.mongodb import connect_mongodb
    from db.redis_client import connect_redis
    from db.vector_db import connect_qdrant
    
    try:
        await connect_mongodb()
        await connect_redis()
        await connect_qdrant()
        logger.info("All database connections initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize databases: {e}")
        raise

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Vectal.ai Clone API...")
    
    # Close database connections
    from db.mongodb import close_mongodb
    from db.redis_client import close_redis
    from db.vector_db import close_qdrant
    from db.postgres import close_db
    
    try:
        await close_mongodb()
        await close_redis()
        await close_qdrant()
        await close_db()
        logger.info("All database connections closed successfully")
    except Exception as e:
        logger.error(f"Error closing databases: {e}")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Vectal.ai Clone API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
