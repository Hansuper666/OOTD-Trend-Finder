import os
import requests
from PIL import Image
from io import BytesIO
import random
import time
import json

# List of fashion image URLs from various public sources
FASHION_IMAGE_URLS = [
    # Sample fashion images from Wikimedia Commons and other public sources
    "https://upload.wikimedia.org/wikipedia/commons/8/87/Fashion_style_outfit.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/3/32/Outfit_of_the_day_women%27s_fashion.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/a/a0/Street_fashion_style_outfit.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/b/b2/Fashion_model_outfit.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/5/54/Summer_outfit_fashion_style.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/c/c5/Street_style_fashion_outfit.jpg",
    # Pixabay Fashion Images (Public Domain/CC0)
    "https://cdn.pixabay.com/photo/2017/08/01/11/48/woman-2564660_1280.jpg",
    "https://cdn.pixabay.com/photo/2016/11/29/09/38/adult-1868750_1280.jpg",
    "https://cdn.pixabay.com/photo/2016/11/22/06/05/girl-1848454_1280.jpg",
    "https://cdn.pixabay.com/photo/2016/11/29/11/24/woman-1869158_1280.jpg",
    "https://cdn.pixabay.com/photo/2016/11/29/11/45/desktop-1869306_1280.jpg",
    "https://cdn.pixabay.com/photo/2015/01/15/13/06/woman-600238_1280.jpg",
    "https://cdn.pixabay.com/photo/2018/01/29/17/01/beautiful-3116587_1280.jpg",
    "https://cdn.pixabay.com/photo/2015/07/09/22/45/young-838891_1280.jpg",
    "https://cdn.pixabay.com/photo/2017/02/08/02/56/booties-2047596_1280.jpg",
    "https://cdn.pixabay.com/photo/2016/03/27/22/22/fashion-1284496_1280.jpg",
    "https://cdn.pixabay.com/photo/2018/03/12/22/15/woman-3221863_1280.jpg",
    "https://cdn.pixabay.com/photo/2017/12/15/18/50/isolated-3021541_1280.jpg",
    # Pexels Fashion Images (Free to use)
    "https://images.pexels.com/photos/934070/pexels-photo-934070.jpeg",
    "https://images.pexels.com/photos/1040945/pexels-photo-1040945.jpeg",
    "https://images.pexels.com/photos/972995/pexels-photo-972995.jpeg",
    "https://images.pexels.com/photos/972804/pexels-photo-972804.jpeg",
    "https://images.pexels.com/photos/932401/pexels-photo-932401.jpeg",
    "https://images.pexels.com/photos/1158670/pexels-photo-1158670.jpeg",
    "https://images.pexels.com/photos/291762/pexels-photo-291762.jpeg",
    "https://images.pexels.com/photos/322207/pexels-photo-322207.jpeg",
    "https://images.pexels.com/photos/1055691/pexels-photo-1055691.jpeg",
    "https://images.pexels.com/photos/1036623/pexels-photo-1036623.jpeg",
    # Unsplash Fashion Images (Free to use under Unsplash license)
    "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f",
    "https://images.unsplash.com/photo-1483985988355-763728e1935b",
    "https://images.unsplash.com/photo-1525507119028-ed4c629a60a3",
    "https://images.unsplash.com/photo-1485968579580-b6d095142e6e",
    "https://images.unsplash.com/photo-1492707892479-7bc8d5a4ee93",
    "https://images.unsplash.com/photo-1469334031218-e382a71b716b",
    "https://images.unsplash.com/photo-1462392246754-28dfa2df8e6b",
    "https://images.unsplash.com/photo-1558769132-cb1aea458c5e",
    "https://images.unsplash.com/photo-1583744946564-b52d01a7e430",
    "https://images.unsplash.com/photo-1587502537104-aac10f5fb6f7",
    "https://images.unsplash.com/photo-1485462537746-965f33f7f6a7",
    "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1",
    "https://images.unsplash.com/photo-1577909238428-918ac6745a1d",
    "https://images.unsplash.com/photo-1581044777550-4cfa60707c03",
    "https://images.unsplash.com/photo-1529139574466-a303027c1d8b",
    "https://images.unsplash.com/photo-1539109136881-3be0616acf4b",
    "https://images.unsplash.com/photo-1551803091-e20673f15770",
    "https://images.unsplash.com/photo-1567401893414-76b7b1e5a7a5",
    "https://images.unsplash.com/photo-1566206091558-7f218b696731",
    "https://images.unsplash.com/photo-1603217040941-9eb5b6e929af",
    "https://images.unsplash.com/photo-1608228088998-57828365d486",
    "https://images.unsplash.com/photo-1604766779654-0d45ffd4dc29",
    "https://images.unsplash.com/photo-1622122201714-77da0ca8e5d2",
    "https://images.unsplash.com/photo-1605086998852-18371c333724",
    "https://images.unsplash.com/photo-1600950207944-0d63e8edbc3f",
    "https://images.unsplash.com/photo-1503342217505-b0a15ec3261c",
    # Additional Pexels Fashion Images
    "https://images.pexels.com/photos/1126993/pexels-photo-1126993.jpeg",
    "https://images.pexels.com/photos/1163194/pexels-photo-1163194.jpeg",
    "https://images.pexels.com/photos/1462637/pexels-photo-1462637.jpeg",
    "https://images.pexels.com/photos/1375736/pexels-photo-1375736.jpeg",
    "https://images.pexels.com/photos/794062/pexels-photo-794062.jpeg",
    "https://images.pexels.com/photos/1021693/pexels-photo-1021693.jpeg",
    "https://images.pexels.com/photos/949670/pexels-photo-949670.jpeg",
    "https://images.pexels.com/photos/1078958/pexels-photo-1078958.jpeg",
    "https://images.pexels.com/photos/1148957/pexels-photo-1148957.jpeg",
    "https://images.pexels.com/photos/914668/pexels-photo-914668.jpeg",
    "https://images.pexels.com/photos/985635/pexels-photo-985635.jpeg",
    "https://images.pexels.com/photos/1192609/pexels-photo-1192609.jpeg",
    "https://images.pexels.com/photos/1187954/pexels-photo-1187954.jpeg",
    "https://images.pexels.com/photos/1759622/pexels-photo-1759622.jpeg",
    "https://images.pexels.com/photos/1488507/pexels-photo-1488507.jpeg",
    # Additional Unsplash Fashion Images
    "https://images.unsplash.com/photo-1496747611176-843222e1e57c",
    "https://images.unsplash.com/photo-1509631179647-0177331693ae",
    "https://images.unsplash.com/photo-1527628217451-b2414a1ee733",
    "https://images.unsplash.com/photo-1515664069236-68a74c369d97",
    "https://images.unsplash.com/photo-1475180098004-ca77a66827be",
    "https://images.unsplash.com/photo-1485218126466-34e6392ec754",
    "https://images.unsplash.com/photo-1500917293891-ef795e70e1f6",
    "https://images.unsplash.com/photo-1545291730-faff8ca1d4b0",
    "https://images.unsplash.com/photo-1550614000-4895a10e1bfd",
    "https://images.unsplash.com/photo-1536766820879-059fec98ec0a",
    "https://images.unsplash.com/photo-1551232864-3f0890e580d9",
    "https://images.unsplash.com/photo-1553754538-466add009c05",
    "https://images.unsplash.com/photo-1554412933-514a83d2f3c8",
    "https://images.unsplash.com/photo-1556306535-0f09a537f0a3",
    "https://images.unsplash.com/photo-1560253023-3ec5d502959f",
    # Additional free to use fashion images
    "https://images.unsplash.com/photo-1523359346063-d879354c0ea5",
    "https://images.unsplash.com/photo-1479064555552-3ef4979f8908",
    "https://images.unsplash.com/photo-1554668048-d0b33c593ba0",
    "https://images.unsplash.com/photo-1550402537-6f7b6189b3b6",
    "https://images.unsplash.com/photo-1543087903-1ac2ec7aa8c5",
    "https://images.unsplash.com/photo-1551232864-7ed5e545b7f9",
    "https://images.unsplash.com/photo-1529139574466-8b46a7d3c6d3",
    "https://images.unsplash.com/photo-1522262229-71f6ec6212ca",
    "https://images.unsplash.com/photo-1571908737296-8b8b9b38194a",
    "https://images.unsplash.com/photo-1573664342184-8d9da8df5cd9",
    "https://images.unsplash.com/photo-1578632292335-df3abbb0d586",
    "https://images.unsplash.com/photo-1520006403909-838d6b92c22e",
    "https://images.unsplash.com/photo-1583846783214-7229a48b1899",
    "https://images.unsplash.com/photo-1588117305388-c2631a279f82",
    "https://images.unsplash.com/photo-1594938298603-c8148c4dae35"
]

def download_image(url, save_dir, index):
    """
    Download image from URL and save to disk
    
    Args:
        url (str): Image URL
        save_dir (str): Directory to save image
        index (int): Image index for filename
        
    Returns:
        str: Path where image was saved or None if failed
    """
    try:
        print(f"Downloading {url}")
        
        # Set user agent to mimic browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, stream=True, timeout=10)
        response.raise_for_status()
        
        # Generate filename with index
        file_extension = os.path.splitext(url.split('/')[-1])[-1]
        if not file_extension or len(file_extension) > 5 or '?' in file_extension:
            file_extension = ".jpg"  # Default to jpg if no extension or invalid extension
            
        filename = f"ootd_{index:03d}{file_extension}"
        save_path = os.path.join(save_dir, filename)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Open image to verify it's valid
        image = Image.open(BytesIO(response.content))
        
        # Save image
        image.save(save_path)
        print(f"Saved to {save_path}")
        
        return save_path
    
    except Exception as e:
        print(f"Error downloading image from {url}: {e}")
        return None

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Download OOTD (Outfit of the Day) images")
    parser.add_argument("--limit", type=int, default=50, 
                       help="Number of images to download (max 50)")
    parser.add_argument("--dir", type=str, default="./ootd_images", 
                       help="Directory to save images")
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.dir, exist_ok=True)
    
    # Limit to available URLs or requested limit
    limit = min(args.limit, len(FASHION_IMAGE_URLS))
    
    # Use all URLs or select a random subset
    if limit == len(FASHION_IMAGE_URLS):
        urls_to_download = FASHION_IMAGE_URLS
    else:
        urls_to_download = random.sample(FASHION_IMAGE_URLS, limit)
    
    print(f"Downloading {len(urls_to_download)} OOTD images...")
    
    # Download images
    downloaded_paths = []
    for i, url in enumerate(urls_to_download):
        path = download_image(url, args.dir, i+1)
        if path:
            downloaded_paths.append(path)
            
        # Add a small delay between downloads
        time.sleep(random.uniform(0.3, 0.8))
    
    print(f"\nDownloaded {len(downloaded_paths)} images to {os.path.abspath(args.dir)}")
    
    # Save metadata
    metadata_path = os.path.join(args.dir, "metadata.json")
    metadata = {
        "total_images": len(downloaded_paths),
        "images": [os.path.basename(path) for path in downloaded_paths if path]
    }
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Saved metadata to {metadata_path}")

if __name__ == "__main__":
    main() 