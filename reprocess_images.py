import os
import sys
from PIL import Image
from dotenv import load_dotenv
import traceback

# Load environment variables
load_dotenv()

# Import after loading env vars
from app.database.models import init_db, get_db, OutfitImage, ImageTag
from app.services.ai_service import ai_service
import json

def reprocess_images():
    """Reprocess images with new CLIP tags"""
    print("Reprocessing images with new CLIP-based analysis...")
    
    # Get database session
    db_generator = get_db()
    db = next(db_generator)
    
    try:
        # Get all images
        outfit_images = db.query(OutfitImage).all()
        print(f"Found {len(outfit_images)} images to reprocess")
        
        for image_obj in outfit_images:
            try:
                print(f"Reprocessing image ID {image_obj.id}: {image_obj.file_path}")
                
                # Load image
                img = Image.open(image_obj.file_path)
                
                # Clear existing tags
                db.query(ImageTag).filter(ImageTag.image_id == image_obj.id).delete()
                
                # Analyze image with CLIP
                analysis_json = ai_service.analyze_image(img)
                analysis = json.loads(analysis_json)
                
                # Add new tags
                for item in analysis["clothing_items"]:
                    tag = ImageTag(
                        image_id=image_obj.id,
                        tag=item,
                        confidence=0.95  # High confidence for clothing items
                    )
                    db.add(tag)
                
                # Add style tag
                style_tag = ImageTag(
                    image_id=image_obj.id,
                    tag=analysis["style"],
                    confidence=0.9  # High confidence for style
                )
                db.add(style_tag)
                
                # Add color tags
                for color in analysis["color_palette"]:
                    tag = ImageTag(
                        image_id=image_obj.id,
                        tag=color,
                        confidence=0.85  # Medium-high confidence for colors
                    )
                    db.add(tag)
                
                # Add occasion tags
                for occasion in analysis["occasions"]:
                    tag = ImageTag(
                        image_id=image_obj.id,
                        tag=occasion,
                        confidence=0.8  # Medium confidence for occasions
                    )
                    db.add(tag)
                
                # Commit changes
                db.commit()
                print(f"  - Tagged with: {', '.join(analysis['clothing_items'])}, {analysis['style']}, {', '.join(analysis['color_palette'])}")
                
            except Exception as e:
                db.rollback()
                print(f"Error reprocessing image {image_obj.id}: {e}")
                traceback.print_exc()
        
        print("\nReprocessing complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
    finally:
        db_generator.close()

if __name__ == "__main__":
    reprocess_images() 