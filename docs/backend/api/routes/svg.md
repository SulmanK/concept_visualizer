# SVG Conversion API

This document describes the SVG conversion endpoints in the Concept Visualizer API.

## Overview

The SVG conversion API provides functionality to convert raster images (PNG, JPEG) to SVG vector format. This is useful for:

- Creating scalable versions of generated concepts
- Preparing images for vector-based editing
- Reducing file size for web display

## Endpoints

### Convert Image to SVG

```
POST /api/svg/convert-to-svg
```

Converts a raster image to SVG format using the vtracer library.

#### Request Body

```json
{
  "image_data": "base64-encoded-image-data",
  "color_mode": "binary",
  "max_size": 800
}
```

Parameters:
- `image_data`: Base64-encoded image data (required)
- `color_mode`: Color mode for conversion - "binary", "color", or "grayscale" (default: "binary")
- `max_size`: Maximum dimension for image resizing (optional)

#### Response

```json
{
  "svg_data": "<svg>...</svg>",
  "success": true,
  "message": "SVG conversion successful"
}
```

#### Example

```python
import requests
import base64

# Read image file
with open("image.png", "rb") as f:
    image_data = base64.b64encode(f.read()).decode("utf-8")

# Make request
response = requests.post(
    "http://localhost:8000/api/svg/convert-to-svg",
    json={
        "image_data": image_data,
        "color_mode": "color",
        "max_size": 1200
    }
)

# Save SVG result
if response.status_code == 200:
    svg_data = response.json()["svg_data"]
    with open("output.svg", "w") as f:
        f.write(svg_data)
```

### Compatibility Endpoint

```
POST /api/svg/convert
```

This is an alias for the `/api/svg/convert-to-svg` endpoint for backward compatibility.

## Implementation Details

### Conversion Process

1. Decode base64 image data
2. Resize image if necessary (using PIL)
3. Convert to SVG using vtracer
4. Fallback to simpler conversion if vtracer fails

### Fallback Mechanism

If the primary conversion with vtracer fails, the API falls back to a simpler conversion method that:
- Creates an SVG with the image embedded as a data URL
- This guarantees that a valid SVG is always returned

### Rate Limiting

The SVG conversion endpoints are rate-limited to 20 requests per hour per session to prevent abuse.

## Error Handling

Common errors:

| Status Code | Error Code | Description |
|-------------|------------|-------------|
| 400 | validation_error | Invalid request (missing image data, invalid format) |
| 429 | rate_limit_exceeded | Rate limit exceeded |
| 503 | service_unavailable | Conversion service failed |

Example error response:

```json
{
  "detail": "Invalid base64 image data",
  "status_code": 400,
  "error_code": "validation_error",
  "field_errors": {
    "image_data": ["Invalid base64 format"]
  }
}
```

## Best Practices

1. **Optimize Images Before Conversion**: Smaller, cleaner images produce better SVG results
2. **Use Binary Mode for Line Art**: Binary mode works best for line drawings or logos
3. **Use Color Mode for Photos**: Color mode preserves more detail in photographs
4. **Implement Client-Side Rate Limiting**: To avoid hitting server-side limits 