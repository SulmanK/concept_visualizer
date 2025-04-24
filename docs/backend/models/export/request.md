# Export Request Models

This documentation covers the request models used for exporting images in different formats.

## Overview

The `request.py` module in `app/models/export/` defines Pydantic models for validating requests to the image export endpoints. These models ensure that all export requests contain the necessary information and meet validation criteria.

## Models

### ExportRequest

```python
class ExportRequest(APIBaseModel):
    """Request model for image export."""

    image_identifier: str = Field(
        ...,
        description="Storage path identifier for the image (e.g., user_id/.../image.png)"
    )
    target_format: Literal["png", "jpg", "svg"] = Field(
        ...,
        description="Target format for export"
    )
    target_size: Literal["small", "medium", "large", "original"] = Field(
        "original",
        description="Target size for export"
    )
    svg_params: Optional[Dict] = Field(
        None,
        description="Optional parameters for SVG conversion (when target_format is 'svg')"
    )
    storage_bucket: str = Field(
        "concept-images",
        description="Storage bucket where the image is stored (concept-images or palette-images)"
    )
```

This model is used for requesting image exports and includes the following fields:

- `image_identifier`: Storage path identifier for the image (e.g., "user_123/concepts/image.png")
- `target_format`: Target format for export (one of: "png", "jpg", "svg")
- `target_size`: Target size for export (one of: "small", "medium", "large", "original", defaults to "original")
- `svg_params`: Optional parameters for SVG conversion when target_format is "svg"
- `storage_bucket`: Storage bucket where the image is stored (one of: "concept-images" or "palette-images", defaults to "concept-images")

## Validators

The model includes custom validators to ensure the data meets specific requirements:

### Image Identifier Validator

```python
@validator("image_identifier")
def validate_image_identifier(cls, v):
    """Validate the image identifier format."""
    # Ensure it's a valid storage path without any URL components
    if "://" in v or "?" in v or v.startswith("/"):
        raise ValueError("image_identifier must be a storage path, not a URL")
    return v
```

This validator ensures that the `image_identifier` is a valid storage path and not a URL by checking for protocol components ("://"), query parameters ("?"), or leading slashes.

### Storage Bucket Validator

```python
@validator("storage_bucket")
def validate_storage_bucket(cls, v):
    """Validate the storage bucket name."""
    valid_buckets = ["concept-images", "palette-images"]
    if v not in valid_buckets:
        raise ValueError(f"storage_bucket must be one of: {', '.join(valid_buckets)}")
    return v
```

This validator ensures that the `storage_bucket` is one of the predefined valid bucket names: "concept-images" or "palette-images".

## Usage Example

```json
{
  "image_identifier": "user_123/concepts/logo_concept_1.png",
  "target_format": "svg",
  "target_size": "large",
  "svg_params": {
    "simplify": true,
    "colors": 5
  },
  "storage_bucket": "concept-images"
}
```

This example requests an SVG export of a concept image, with a large size and specific SVG conversion parameters.

## Endpoints Using This Model

The `ExportRequest` model is primarily used by the export endpoints in the API:

- `POST /api/export/image`: Export an image to the specified format and size

## Related Files

- [Export Service](../../services/export/service.md): Service implementing export functionality
- [Export Interface](../../services/export/interface.md): Interface definition for export services
- [Export Routes](../../api/routes/export/export_routes.md): API routes for export functionality
