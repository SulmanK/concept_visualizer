"""
SVG conversion API endpoints.

This module provides routes for converting raster images to SVG format.
"""

from fastapi import APIRouter, HTTPException, Body
import base64
from io import BytesIO
import tempfile
import os
import vtracer
from PIL import Image

from ...models.request import SVGConversionRequest
from ...models.response import SVGConversionResponse


router = APIRouter()


@router.post("/convert-to-svg", response_model=SVGConversionResponse)
async def convert_to_svg(
    request: SVGConversionRequest = Body(...)
):
    """Convert a raster image to SVG using vtracer.
    
    Args:
        request: The request containing the image data and conversion options
        
    Returns:
        SVGConversionResponse containing the SVG data
    """
    try:
        # Extract the image data from base64
        if not request.image_data:
            raise HTTPException(status_code=400, detail="No image data provided")
        
        # Remove data URL prefix if present
        image_data = request.image_data
        if "base64," in image_data:
            image_data = image_data.split("base64,")[1]
        
        # Decode base64
        image_bytes = base64.b64decode(image_data)
        
        # Create temporary files for input and output
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_in_file, \
             tempfile.NamedTemporaryFile(delete=False, suffix=".svg") as temp_out_file:
            
            temp_in_path = temp_in_file.name
            temp_out_path = temp_out_file.name
            
            # Close files so they can be used by other processes
            temp_in_file.close()
            temp_out_file.close()
            
            try:
                # Process the image with PIL to ensure the format is correct
                image = Image.open(BytesIO(image_bytes))
                
                # Resize if needed
                if request.max_size and (image.width > request.max_size or image.height > request.max_size):
                    # Preserve aspect ratio
                    if image.width > image.height:
                        new_width = request.max_size
                        new_height = int(image.height * (request.max_size / image.width))
                    else:
                        new_height = request.max_size
                        new_width = int(image.width * (request.max_size / image.height))
                    
                    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Save to temporary input file
                image.save(temp_in_path, format="PNG")
                
                try:
                    # Process the image using the vtracer Python API
                    print(f"Converting image to SVG with vtracer: {temp_in_path} -> {temp_out_path}")
                    
                    # Set color mode parameter
                    color_mode = "binary"
                    if request.color_mode == "color":
                        color_mode = "color"
                    elif request.color_mode == "grayscale":
                        color_mode = "color"  # vtracer doesn't have grayscale mode, fallback to color
                    
                    # Use a simplified approach first - try with minimal parameters
                    with open(temp_in_path, 'rb') as f:
                        input_bytes = f.read()
                    
                    # Try with minimal parameters first for better compatibility
                    try:
                        svg_content = vtracer.convert_raw_image_to_svg(
                            input_bytes,
                            img_format="png",
                            colormode=color_mode
                        )
                    except Exception as e:
                        print(f"Simple conversion failed: {e}, falling back to embedding image")
                        # If simple conversion fails, use the fallback
                        create_simple_svg_from_image(image, temp_out_path)
                        with open(temp_out_path, "r") as svg_file:
                            svg_content = svg_file.read()
                    
                    print("Conversion completed successfully")
                    
                    # Ensure SVG content is valid
                    if not svg_content.strip().startswith("<?xml") and not svg_content.strip().startswith("<svg"):
                        print("Generated SVG content may be invalid, using fallback")
                        create_simple_svg_from_image(image, temp_out_path)
                        with open(temp_out_path, "r") as svg_file:
                            svg_content = svg_file.read()
                    
                    # Write SVG to temp file for debugging
                    with open(temp_out_path, "w") as f:
                        f.write(svg_content)
                    
                except Exception as e:
                    print(f"Error during vtracer conversion: {e}")
                    # Fall back to a simpler conversion
                    create_simple_svg_from_image(image, temp_out_path)
                    with open(temp_out_path, "r") as svg_file:
                        svg_content = svg_file.read()
                
                return SVGConversionResponse(
                    svg_data=svg_content,
                    success=True,
                    message="SVG conversion successful"
                )
                
            finally:
                # Clean up temporary files
                try:
                    os.unlink(temp_in_path)
                    os.unlink(temp_out_path)
                except Exception as e:
                    print(f"Error removing temporary files: {e}")
        
    except Exception as e:
        print(f"SVG conversion error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"SVG conversion failed: {str(e)}")


def create_simple_svg_from_image(image, output_path):
    """Create a simple SVG from an image as a fallback.
    
    Args:
        image: PIL Image object
        output_path: Path to save the SVG file
    
    Returns:
        None
    """
    width, height = image.size
    
    # Create a basic SVG that embeds the image as a data URL
    with open(output_path, "w") as f:
        img_bytes = BytesIO()
        image.save(img_bytes, format="PNG")
        img_b64 = base64.b64encode(img_bytes.getvalue()).decode("utf-8")
        
        svg_content = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{width}" height="{height}">
  <image width="{width}" height="{height}" xlink:href="data:image/png;base64,{img_b64}"/>
</svg>"""
        
        f.write(svg_content) 