from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from PIL import Image

from ..database.models import get_db, OutfitImage
from ..services.image_service import image_service
from ..services.ai_service import ai_service
from ..utils.image_utils import save_uploaded_image
from ..config.settings import settings

router = APIRouter()

# Model schemas for request/response
from pydantic import BaseModel

class TagResponse(BaseModel):
    tag: str
    confidence: float
    
class ImageResponse(BaseModel):
    id: int
    url: str
    file_path: str
    source: str
    tags: List[TagResponse]
    
    class Config:
        orm_mode = True

class SearchResponse(BaseModel):
    id: int
    url: str
    file_path: str
    source: str
    similarity: float
    tags: List[TagResponse]
    
    class Config:
        orm_mode = True

class AnalysisResponse(BaseModel):
    clothing_items: List[str]
    style: str
    color_palette: List[str]
    occasions: List[str]
    
    class Config:
        orm_mode = True

@router.post("/fetch-ootd-images", status_code=202)
async def fetch_ootd_images(
    background_tasks: BackgroundTasks,
    query: str = Query(default=settings.PINTEREST_SEARCH_TERM, description="Search query for OOTD images"),
    limit: int = Query(default=settings.PINTEREST_SEARCH_LIMIT, description="Maximum number of images to fetch"),
    db: Session = Depends(get_db)
):
    """
    Fetch OOTD images from Pinterest and process them (runs in background)
    """
    # Add task to background so response can be returned immediately
    background_tasks.add_task(image_service.fetch_and_process_images, db, query, limit)
    
    return {"message": f"Fetching {limit} images for query '{query}'. This process runs in the background and may take some time."}

@router.get("/images", response_model=List[ImageResponse])
async def get_images(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all OOTD images
    """
    images = image_service.get_all_images(db, skip, limit)
    
    # Convert to response model
    result = []
    for image in images:
        tags = [TagResponse(tag=tag.tag, confidence=tag.confidence) for tag in image.tags]
        result.append(ImageResponse(
            id=image.id,
            url=image.url,
            file_path=image.file_path,
            source=image.source,
            tags=tags
        ))
    
    return result

@router.get("/image/{image_id}", response_class=FileResponse)
async def get_image(
    image_id: int,
    db: Session = Depends(get_db)
):
    """
    Get image file by ID
    """
    image = db.query(OutfitImage).filter(OutfitImage.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(image.file_path)

@router.post("/search/text", response_model=List[SearchResponse])
async def search_by_text(
    query: str = Form(...),
    limit: int = Form(5),
    db: Session = Depends(get_db)
):
    """
    Search for OOTD images using text query
    """
    results = ai_service.search_by_text(db, query, limit)
    
    # Convert to response model
    response = []
    for image, similarity in results:
        tags = [TagResponse(tag=tag.tag, confidence=tag.confidence) for tag in image.tags]
        response.append(SearchResponse(
            id=image.id,
            url=image.url,
            file_path=image.file_path,
            source=image.source,
            similarity=float(similarity),
            tags=tags
        ))
    
    return response

@router.post("/search/image", response_model=List[SearchResponse])
async def search_by_image(
    file: UploadFile = File(...),
    limit: int = Form(5),
    db: Session = Depends(get_db)
):
    """
    Search for OOTD images using uploaded image
    """
    # Save uploaded image
    file_path = save_uploaded_image(file)
    
    # Open image
    query_image = Image.open(file_path)
    
    # Search for similar images
    results = ai_service.search_by_image(db, query_image, limit)
    
    # Convert to response model
    response = []
    for image, similarity in results:
        tags = [TagResponse(tag=tag.tag, confidence=tag.confidence) for tag in image.tags]
        response.append(SearchResponse(
            id=image.id,
            url=image.url,
            file_path=image.file_path,
            source=image.source,
            similarity=float(similarity),
            tags=tags
        ))
    
    return response

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_image(
    file: UploadFile = File(...)
):
    """
    Analyze uploaded clothing image
    """
    # Save uploaded image
    file_path = save_uploaded_image(file)
    
    # Open image
    image = Image.open(file_path)
    
    # Analyze image
    analysis_json = ai_service.analyze_image(image)
    
    # Parse JSON response
    import json
    analysis = json.loads(analysis_json)
    
    return AnalysisResponse(
        clothing_items=analysis.get("clothing_items", []),
        style=analysis.get("style", ""),
        color_palette=analysis.get("color_palette", []),
        occasions=analysis.get("occasions", [])
    ) 