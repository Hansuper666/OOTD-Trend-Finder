import os
import sys
import traceback
from dotenv import load_dotenv
import argparse

# Load environment variables
load_dotenv()

print("Environment variables loaded")

# Import after loading env vars
try:
    from app.database.models import init_db, get_db
    from app.services.image_service import image_service
    print("Successfully imported required modules")
except Exception as e:
    print(f"Error importing modules: {e}")
    traceback.print_exc()
    sys.exit(1)

def download_ootd_images(query="outfit of the day", limit=50):
    """Download and process OOTD images"""
    print(f"Setting up to download {limit} OOTD images for query: '{query}'...")
    
    try:
        # Initialize the database if it doesn't exist
        print("Initializing database...")
        init_db()
        print("Database initialized")
        
        # Get database session
        print("Getting database session...")
        db_generator = get_db()
        db = next(db_generator)
        print("Database session created")
        
        try:
            # Fetch and process images
            print("Starting image download and processing...")
            processed_count = image_service.fetch_and_process_images(db, query, limit)
            print(f"Successfully processed {processed_count} images.")
            
            # Get the directory where images are stored
            storage_path = os.path.abspath(image_service.storage_path)
            print(f"Images are stored in: {storage_path}")
            
        except Exception as e:
            print(f"Error downloading images: {e}")
            traceback.print_exc()
        finally:
            print("Closing database session...")
            db_generator.close()
            print("Database session closed")
    except Exception as e:
        print(f"Error in download_ootd_images: {e}")
        traceback.print_exc()

def main():
    parser = argparse.ArgumentParser(description="Download OOTD (Outfit of the Day) images")
    parser.add_argument("--query", type=str, default="outfit of the day fashion style", 
                        help="Search query for OOTD images")
    parser.add_argument("--limit", type=int, default=50, 
                        help="Number of images to download")
    
    args = parser.parse_args()
    print(f"Arguments parsed: query='{args.query}', limit={args.limit}")
    
    download_ootd_images(args.query, args.limit)
    
    print("\nDownload complete!")
    print("You can now use the OOTD app to search through these images.")
    print("Run 'uvicorn app.main:app --reload' to start the application.")

if __name__ == "__main__":
    print("Starting OOTD image download script...")
    main()
    print("Script execution completed") 