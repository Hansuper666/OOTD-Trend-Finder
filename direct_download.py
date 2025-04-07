import os
import requests
from PIL import Image
from io import BytesIO
import uuid
import argparse
import json
import random
import time
from bs4 import BeautifulSoup
import re

def download_image(url, save_dir):
    """
    Download image from URL and save to disk
    
    Args:
        url (str): Image URL
        save_dir (str): Directory to save image
        
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
        
        # Generate a unique filename
        file_extension = os.path.splitext(url.split('/')[-1])[-1]
        if not file_extension or len(file_extension) > 5:
            file_extension = ".jpg"  # Default to jpg if no extension or invalid extension
            
        filename = f"ootd_{uuid.uuid4()}{file_extension}"
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

def fetch_bing_images(query, limit=50):
    """
    Fetch image URLs from Bing Image Search
    
    Args:
        query (str): Search query
        limit (int): Maximum number of images to fetch
        
    Returns:
        list: List of image URLs
    """
    print(f"Searching for '{query}' images on Bing...")
    
    # Format query for URL
    query = query.replace(' ', '+')
    
    # Set up headers to mimic browser request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.bing.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    image_urls = []
    page = 1
    
    while len(image_urls) < limit:
        # Build URL for current page
        if page == 1:
            url = f"https://www.bing.com/images/search?q={query}&form=HDRSC2&first=1"
        else:
            url = f"https://www.bing.com/images/search?q={query}&form=HDRSC2&first={1 + (page-1)*35}"
        
        try:
            print(f"Fetching page {page}...")
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find image elements - Bing image search uses m elements with class mimg
            image_elements = soup.select('.mimg')
            
            if not image_elements:
                # Try alternative selectors if the first one doesn't work
                image_elements = soup.select('a.iusc')
            
            if not image_elements:
                print(f"No image elements found on page {page}")
                break
                
            for img in image_elements:
                # Extract image URL from data-src attribute or src attribute
                img_url = None
                
                # Try to find the URL in the data attributes
                if img.has_attr('data-src'):
                    img_url = img['data-src']
                elif img.has_attr('src'):
                    img_url = img['src']
                elif img.has_attr('m'):
                    try:
                        # In some cases, the URL is in a JSON string in the m attribute
                        m_json = json.loads(img['m'])
                        if 'murl' in m_json:
                            img_url = m_json['murl']
                    except:
                        pass
                
                # If still haven't found URL, look in parent elements
                if not img_url and img.parent and img.parent.has_attr('href'):
                    href = img.parent['href']
                    match = re.search(r'imgurl=([^&]+)', href)
                    if match:
                        img_url = requests.utils.unquote(match.group(1))
                
                if img_url and img_url.startswith(('http://', 'https://')):
                    image_urls.append(img_url)
                    if len(image_urls) >= limit:
                        break
            
            # If we didn't find any images on this page, break
            if len(image_urls) == 0:
                break
                
            # Move to next page
            page += 1
            
            # Add a small delay to avoid being blocked
            time.sleep(random.uniform(1, 3))
                
        except Exception as e:
            print(f"Error fetching images from Bing: {e}")
            break
    
    # Make sure URLs are unique
    image_urls = list(dict.fromkeys(image_urls))
    
    print(f"Found {len(image_urls)} image URLs from Bing")
    return image_urls[:limit]

def main():
    parser = argparse.ArgumentParser(description="Download OOTD (Outfit of the Day) images")
    parser.add_argument("--query", type=str, default="outfit of the day fashion style trend", 
                       help="Search query for OOTD images")
    parser.add_argument("--limit", type=int, default=50, 
                       help="Number of images to download")
    parser.add_argument("--dir", type=str, default="./ootd_images", 
                       help="Directory to save images")
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.dir, exist_ok=True)
    
    # Fetch image URLs from Bing
    image_urls = fetch_bing_images(args.query, args.limit)
    
    print(f"Found {len(image_urls)} images to download")
    
    # Download images
    downloaded_paths = []
    for url in image_urls:
        path = download_image(url, args.dir)
        if path:
            downloaded_paths.append(path)
            
        # Add a small delay between downloads
        time.sleep(random.uniform(0.5, 1.5))
    
    print(f"\nDownloaded {len(downloaded_paths)} images to {os.path.abspath(args.dir)}")
    
    # Save metadata
    metadata_path = os.path.join(args.dir, "metadata.json")
    metadata = {
        "query": args.query,
        "total_images": len(downloaded_paths),
        "images": [os.path.basename(path) for path in downloaded_paths if path]
    }
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Saved metadata to {metadata_path}")

if __name__ == "__main__":
    main() 