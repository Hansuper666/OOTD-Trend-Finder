import os
import json
from PIL import Image

def get_image_count(directory):
    """Count the number of image files in a directory"""
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    valid_images = []
    
    try:
        # List all files in the directory
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        
        # Filter for image files
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in image_extensions:
                file_path = os.path.join(directory, file)
                try:
                    # Verify it's a valid image by opening it
                    with Image.open(file_path) as img:
                        valid_images.append(file)
                except Exception as e:
                    print(f"Skipping invalid image {file}: {e}")
    
    except Exception as e:
        print(f"Error scanning directory: {e}")
    
    return valid_images

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Count image files in a directory")
    parser.add_argument("--dir", type=str, default="./ootd_images", 
                       help="Directory containing image files")
    
    args = parser.parse_args()
    
    # Get list of valid images
    print(f"Scanning directory: {args.dir}")
    image_files = get_image_count(args.dir)
    
    # Sort image files
    image_files.sort()
    
    print(f"\nFound {len(image_files)} valid image files")
    
    # Save metadata
    metadata_path = os.path.join(args.dir, "merged_metadata.json")
    metadata = {
        "total_images": len(image_files),
        "images": image_files
    }
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Saved metadata to {metadata_path}")
    
    # Print the first 10 and last 10 images
    if len(image_files) > 20:
        print("\nFirst 10 images:")
        for img in image_files[:10]:
            print(f"  {img}")
        
        print("\nLast 10 images:")
        for img in image_files[-10:]:
            print(f"  {img}")
    else:
        print("\nAll images:")
        for img in image_files:
            print(f"  {img}")
    
if __name__ == "__main__":
    main() 