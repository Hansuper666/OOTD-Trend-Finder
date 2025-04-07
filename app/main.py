from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import os

from .config.settings import settings
from .database.models import init_db, get_db
from .api.endpoints import router as api_router

# Create directories if they don't exist
os.makedirs(settings.IMAGE_STORAGE_PATH, exist_ok=True)
os.makedirs(settings.UPLOAD_PATH, exist_ok=True)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include API routes
app.include_router(api_router, prefix="/api")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

# Home route - redirect to static HTML
@app.get("/")
async def home():
    return RedirectResponse(url="/static/index.html")

# API documentation route
@app.get("/api-docs")
async def api_docs():
    return {
        "message": "API Documentation",
        "docs_url": "/docs"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 