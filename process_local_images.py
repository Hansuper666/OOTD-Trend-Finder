import os
import sys
from PIL import Image
from dotenv import load_dotenv
import traceback

# Load environment variables
load_dotenv()

# Import after loading env vars
from app.database.models import init_db, get_db
from app.services.ai_service import ai_service

def process_local_images(image_dir="./ootd_images"):
    """Process local OOTD images"""
    print(f"Processing images from directory: {image_dir}")
    
    # Initialize the database
    print("Initializing database...")
    init_db()
    
    # Get database session
    print("Getting database session...")
    db_generator = get_db()
    db = next(db_generator)
    
    try:
        # Get list of image files
        image_files = [f for f in os.listdir(image_dir) 
                      if os.path.isfile(os.path.join(image_dir, f)) 
                      and f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        print(f"Found {len(image_files)} image files")
        
        # Prepare images for processing
        images_to_process = []
        for filename in image_files:
            try:
                file_path = os.path.join(image_dir, filename)
                image = Image.open(file_path)
                
                # Create image data dictionary
                img_data = {
                    "image": image,
                    "path": file_path,
                    "url": f"local://{filename}",  # Local reference
                    "source": "local"
                }
                
                images_to_process.append(img_data)
                print(f"Prepared image: {filename}")
            except Exception as e:
                print(f"Error loading image {filename}: {e}")
        
        # Import image service here to avoid circular import
        from app.services.image_service import image_service
        
        # Process the images in batches to avoid memory issues
        batch_size = 10
        total_processed = 0
        
        for i in range(0, len(images_to_process), batch_size):
            batch = images_to_process[i:i+batch_size]
            print(f"Processing batch {i//batch_size + 1}/{(len(images_to_process)-1)//batch_size + 1} ({len(batch)} images)...")
            
            # Process the batch of images
            processed_count = image_service.process_images(db, batch)
            total_processed += processed_count
            
            print(f"Processed {processed_count} images in this batch")
        
        print(f"\nTotal images successfully processed: {total_processed}")
        
    except Exception as e:
        print(f"Error processing images: {e}")
        traceback.print_exc()
    finally:
        print("Closing database session...")
        db_generator.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Process local OOTD images")
    parser.add_argument("--dir", type=str, default="./ootd_images", 
                       help="Directory containing image files")
    
    args = parser.parse_args()
    process_local_images(args.dir) 