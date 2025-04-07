import os
import uuid
import requests
from PIL import Image
from io import BytesIO
import numpy as np
import hashlib
from ..config.settings import settings

def download_image(url, save_path=None):
    """
    Download image from URL and optionally save to disk
    
    Args:
        url (str): Image URL
        save_path (str, optional): Path to save image. If None, image is not saved.
        
    Returns:
        PIL.Image: Downloaded image
        str: Path where image was saved (if save_path provided)
    """
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        
        image = Image.open(BytesIO(response.content))
        
        if save_path:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # Save image
            image.save(save_path)
            return image, save_path
        
        return image, None
    
    except Exception as e:
        print(f"Error downloading image from {url}: {e}")
        return None, None

def save_uploaded_image(file, upload_dir=settings.UPLOAD_PATH):
    """
    Save an uploaded image file
    
    Args:
        file: UploadFile from FastAPI
        upload_dir (str): Directory to save the uploaded file
        
    Returns:
        str: Path where the image was saved
    """
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate a unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save the file
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    
    return file_path

def preprocess_image(image):
    """
    Preprocess image for AI model input
    
    Args:
        image (PIL.Image): Image to preprocess
        
    Returns:
        np.ndarray: Preprocessed image
    """
    # Resize to standard size
    image = image.resize((224, 224))
    
    # Convert to RGB if not already
    if image.mode != "RGB":
        image = image.convert("RGB")
    
    # Convert to numpy array and normalize
    img_array = np.array(image)
    img_array = img_array / 255.0  # Normalize to [0,1]
    
    return img_array

def get_image_hash(image):
    """
    Create a hash for an image to check for duplicates
    
    Args:
        image (PIL.Image): Image to hash
        
    Returns:
        str: Hash of the image
    """
    # Resize image to small dimension for faster hashing
    image = image.resize((32, 32), Image.LANCZOS)
    image = image.convert("L")  # Convert to grayscale
    
    # Get image data as bytes
    img_data = np.array(image).tobytes()
    
    # Create hash
    return hashlib.md5(img_data).hexdigest() 