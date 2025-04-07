import os
import sys
from dotenv import load_dotenv
import argparse

# Load environment variables
load_dotenv()

# Import after loading env vars
from app.database.models import init_db, get_db
from app.services.image_service import image_service

def setup_database():
    """Initialize the database schema"""
    print("Initializing database...")
    init_db()
    print("Database initialized successfully.")

def fetch_initial_images(query="outfit of the day", limit=50):
    """Fetch and process initial OOTD images"""
    print(f"Fetching {limit} images for query: '{query}'...")
    
    # Get database session
    db_generator = get_db()
    db = next(db_generator)
    
    try:
        # Fetch and process images
        processed_count = image_service.fetch_and_process_images(db, query, limit)
        print(f"Successfully processed {processed_count} images.")
    except Exception as e:
        print(f"Error fetching images: {e}")
    finally:
        db_generator.close()

def main():
    parser = argparse.ArgumentParser(description="Initialize OOTD Trend Finder application")
    parser.add_argument("--skip-db", action="store_true", help="Skip database initialization")
    parser.add_argument("--skip-images", action="store_true", help="Skip initial image fetching")
    parser.add_argument("--query", type=str, default="outfit of the day", 
                        help="Search query for initial images")
    parser.add_argument("--limit", type=int, default=50, 
                        help="Maximum number of images to fetch")
    
    args = parser.parse_args()
    
    if not args.skip_db:
        setup_database()
    
    if not args.skip_images:
        fetch_initial_images(args.query, args.limit)
    
    print("Initialization complete!")
    print("Run 'uvicorn app.main:app --reload' to start the application.")

if __name__ == "__main__":
    main() 