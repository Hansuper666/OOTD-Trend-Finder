import os
import requests
import json
import uuid
from PIL import Image
from sqlalchemy.orm import Session
from ..database.models import OutfitImage, ImageFeature, ImageTag
from ..utils.image_utils import download_image, get_image_hash
from ..config.settings import settings
from .ai_service import ai_service

class ImageService:
    def __init__(self):
        self.api_key = settings.PINTEREST_API_KEY
        self.storage_path = settings.IMAGE_STORAGE_PATH
        
        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_path, exist_ok=True)
    
    def fetch_pinterest_images(self, query="outfit of the day", limit=50):
        """
        Fetch outfit images from Unsplash instead of Pinterest
        
        Args:
            query (str): Search query
            limit (int): Maximum number of images to fetch
            
        Returns:
            list: List of image URLs
        """
        # Using Unsplash API to get real images
        print(f"Fetching {limit} OOTD images from Unsplash with query: '{query}'")
        
        # Unsplash API endpoint - using the public access demo key
        # For production, you should register for your own API key at https://unsplash.com/developers
        access_key = "702b23d32a3cf8c9f5d0dc0048644a3a41ffd8f93a8058d1b86a8aa24fcd12a3"
        url = f"https://api.unsplash.com/search/photos"
        
        # Parameters for the API request
        params = {
            "query": query,
            "per_page": min(30, limit),  # API limits to 30 per page
            "client_id": access_key,
            "content_filter": "high"
        }
        
        image_urls = []
        page = 1
        
        # Fetch images across multiple pages if needed
        while len(image_urls) < limit:
            params["page"] = page
            
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                # Extract image URLs from response
                results = data.get("results", [])
                if not results:
                    break
                
                for photo in results:
                    # Get the regular sized image URL
                    image_url = photo.get("urls", {}).get("regular")
                    if image_url:
                        image_urls.append(image_url)
                        
                        if len(image_urls) >= limit:
                            break
                
                # Move to next page
                page += 1
                
                # Check if we've reached the last page
                if page > data.get("total_pages", 1) or not data.get("results"):
                    break
                    
            except Exception as e:
                print(f"Error fetching images from Unsplash: {e}")
                break
        
        # If we couldn't get enough images from Unsplash, try Pexels as a backup
        if len(image_urls) < limit:
            print(f"Only found {len(image_urls)} images on Unsplash, trying Pexels...")
            pexels_urls = self._fetch_from_pexels(query, limit - len(image_urls))
            image_urls.extend(pexels_urls)
        
        print(f"Successfully retrieved {len(image_urls)} image URLs")
        return image_urls
    
    def _fetch_from_pexels(self, query="outfit fashion", limit=20):
        """
        Fetch images from Pexels as a backup source
        
        Args:
            query (str): Search query
            limit (int): Maximum number of images to fetch
            
        Returns:
            list: List of image URLs
        """
        # Pexels API endpoint - using a demo key
        # For production, register at https://www.pexels.com/api/
        api_key = "563492ad6f91700001000001b3c9c10c5ab84a25b026f4b39d4a8f21"
        url = "https://api.pexels.com/v1/search"
        
        headers = {
            "Authorization": api_key
        }
        
        params = {
            "query": query,
            "per_page": min(80, limit),
        }
        
        image_urls = []
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Extract image URLs from response
            photos = data.get("photos", [])
            
            for photo in photos:
                # Get the medium sized image URL
                image_url = photo.get("src", {}).get("medium")
                if image_url:
                    image_urls.append(image_url)
                    
                    if len(image_urls) >= limit:
                        break
                        
        except Exception as e:
            print(f"Error fetching images from Pexels: {e}")
        
        return image_urls
    
    def download_images(self, urls, source="pinterest"):
        """
        Download images from URLs and return successfully downloaded ones
        
        Args:
            urls (list): List of image URLs
            source (str): Source of the images
            
        Returns:
            list: List of downloaded image paths
        """
        downloaded_images = []
        
        for url in urls:
            # Generate a unique filename
            file_extension = os.path.splitext(url.split('/')[-1])[-1]
            if not file_extension:
                file_extension = ".jpg"  # Default to jpg if no extension
                
            filename = f"{uuid.uuid4()}{file_extension}"
            save_path = os.path.join(self.storage_path, filename)
            
            # Download the image
            image, path = download_image(url, save_path)
            
            if image and path:
                downloaded_images.append({
                    "image": image,
                    "path": path,
                    "url": url,
                    "source": source
                })
        
        return downloaded_images
    
    def process_images(self, db: Session, images):
        """
        Process downloaded images, generate embeddings, extract tags, and store in database
        
        Args:
            db (Session): Database session
            images (list): List of downloaded image dictionaries
            
        Returns:
            int: Number of images processed
        """
        processed_count = 0
        
        # Get existing image hashes to avoid duplicates
        existing_images = db.query(OutfitImage).all()
        existing_hashes = {}
        
        for image_obj in existing_images:
            try:
                img = Image.open(image_obj.file_path)
                existing_hashes[get_image_hash(img)] = True
            except Exception as e:
                print(f"Error loading image {image_obj.file_path}: {e}")
        
        for img_data in images:
            try:
                # Check if image is a duplicate
                img_hash = get_image_hash(img_data["image"])
                if img_hash in existing_hashes:
                    print(f"Skipping duplicate image: {img_data['url']}")
                    continue
                
                # Add to database
                outfit_image = OutfitImage(
                    url=img_data["url"],
                    file_path=img_data["path"],
                    source=img_data["source"]
                )
                
                db.add(outfit_image)
                db.flush()  # Get ID before committing
                
                # Generate embedding
                embedding = ai_service.generate_image_embedding(img_data["image"])
                
                # Add embedding to database
                image_feature = ImageFeature(
                    image_id=outfit_image.id,
                    embedding=embedding.tobytes()
                )
                db.add(image_feature)
                
                # Extract and add tags
                tags = ai_service.get_tags_for_image(img_data["image"])
                for tag, confidence in tags:
                    image_tag = ImageTag(
                        image_id=outfit_image.id,
                        tag=tag,
                        confidence=confidence
                    )
                    db.add(image_tag)
                
                db.commit()
                processed_count += 1
                existing_hashes[img_hash] = True  # Add to existing hashes to avoid duplicates in this batch
                
            except Exception as e:
                db.rollback()
                print(f"Error processing image {img_data['url']}: {e}")
        
        return processed_count
    
    def fetch_and_process_images(self, db: Session, query="outfit of the day", limit=50):
        """
        Fetch images from Pinterest and process them
        
        Args:
            db (Session): Database session
            query (str): Search query
            limit (int): Maximum number of images to fetch
            
        Returns:
            int: Number of images processed
        """
        # Fetch image URLs
        urls = self.fetch_pinterest_images(query, limit)
        
        # Download images
        downloaded_images = self.download_images(urls)
        
        # Process images
        return self.process_images(db, downloaded_images)
    
    def get_all_images(self, db: Session, skip=0, limit=100):
        """
        Get all outfit images from the database
        
        Args:
            db (Session): Database session
            skip (int): Number of images to skip
            limit (int): Maximum number of images to return
            
        Returns:
            list: List of OutfitImage objects
        """
        return db.query(OutfitImage).offset(skip).limit(limit).all()

image_service = ImageService() 