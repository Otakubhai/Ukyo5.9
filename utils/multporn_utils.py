"""
Multporn utilities - Functions for scraping and downloading images from multporn.net
"""

import requests
import tempfile
from bs4 import BeautifulSoup

def scrape_images(url):
    """
    Scrapes image URLs from a given URL.

    Args:
        url (str): The URL to scrape images from.

    Returns:
        tuple: A tuple containing a list of image URLs and an error message (if any).
    """
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            return None, f"Failed to fetch the page (Status code: {response.status_code})."

        soup = BeautifulSoup(response.text, "html.parser")
        
        # Find all image tags
        image_tags = soup.find_all("img")
        
        # Extract image URLs
        image_urls = []
        for img in image_tags:
            src = img.get("src")
            if src and any(ext in src.lower() for ext in [".jpg", ".jpeg", ".png"]):
                # Make sure we have the full URL
                image_urls.append(src if src.startswith("http") else "https://multporn.net" + src)
        
        # If we found no images
        if not image_urls:
            return None, "No images found on the page."
            
        return image_urls, None
        
    except Exception as e:
        return None, f"Error scraping images: {str(e)}"

def download_image(url):
    """
    Downloads an image from a URL and saves it to a temporary file.

    Args:
        url (str): The URL of the image to download.

    Returns:
        str: The path to the downloaded image file, or None if download failed.
    """
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    
    try:
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        
        if response.status_code == 200:
            # Determine file extension
            ext = ".jpg"  # Default
            if ".png" in url.lower():
                ext = ".png"
            elif ".jpeg" in url.lower():
                ext = ".jpeg"
                
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
            
            # Download the image in chunks
            with open(temp_file.name, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        
            return temp_file.name
            
    except Exception as e:
        print(f"Error downloading image {url}: {str(e)}")
        
    return None
