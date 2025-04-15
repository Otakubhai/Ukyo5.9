"""
PDF utilities - Functions for creating PDFs from images
"""

import os
from PIL import Image

def create_pdf_from_images(folder_path, output_pdf_path):
    """
    Creates a PDF from images in a folder.

    Args:
        folder_path (str): Path to the folder containing images.
        output_pdf_path (str): Path to save the generated PDF.

    Returns:
        str: Path to the generated PDF.

    Raises:
        Exception: If no valid images are found in the folder.
    """
    # Find all image files and sort them numerically
    image_files = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            try:
                # Extract the number part from the filename
                file_num = int(os.path.splitext(filename)[0])
                image_files.append((filename, file_num))
            except ValueError:
                # If the filename doesn't have a numeric part, just append it
                image_files.append((filename, float('inf')))
    
    # Sort images by their numeric value
    image_files.sort(key=lambda x: x[1])
    
    # Load images
    image_list = []
    for filename, _ in image_files:
        try:
            image_path = os.path.join(folder_path, filename)
            img = Image.open(image_path)
            # Convert to RGB (required for PDF)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            image_list.append(img)
        except Exception as e:
            print(f"Error processing image {filename}: {str(e)}")
    
    # Check if we have any valid images
    if not image_list:
        raise Exception("No valid images found in folder.")
    
    # Save the PDF
    image_list[0].save(
        output_pdf_path,
        save_all=True,
        append_images=image_list[1:],
        resolution=100.0,
        quality=85
    )
    
    return output_pdf_path
