import os
import base64
from fastapi import HTTPException
from pydantic import BaseModel
import sys

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

class ImageResponse(BaseModel):
    filename: str
    content: str  # Base64-encoded image content
    content_type: str

class ImageRequest(BaseModel):
    image_name: str
    
    
def get_image_by_name(image_name: str) -> ImageResponse:
    """
    Get an image from local storage by its name and return it as a Base64-encoded response.
    
    Args:
        image_name (str): Name of the image file.
    
    Returns:
        ImageResponse: The response containing the image filename, Base64 content, and content type.
    """
    
    image_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "...", image_name))
    absolute_image_path = os.path.abspath(image_path)

    # Check if the file exists
    if not os.path.exists(absolute_image_path):
        raise HTTPException(status_code=404, detail=f"Image not found: {absolute_image_path}")
    
    try:
        with open(absolute_image_path, "rb") as file:
            file_data = file.read()
            encoded_content = base64.b64encode(file_data).decode("utf-8")
        
        # Determine the content type based on file extension
        content_type = "image/png" if image_name.lower().endswith(".png") else "image/jpeg"

        return ImageResponse(
            filename=image_name,
            content=encoded_content,
            content_type=content_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading the image: {str(e)}")
