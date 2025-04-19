# Semantic Segmentation for Improved Palette Application

## Problem Statement

Our current color palette application approach uses dominant color detection and HSV color masking, which has several limitations:
- It doesn't respect object boundaries (treats all blue areas the same regardless of whether they're background, clothing, etc.)
- It applies colors based on frequency rather than semantic meaning
- Details and textures are often lost in the transformation
- The results can appear cartoonish and unrealistic

## Proposed Solution

We propose implementing semantic segmentation to identify meaningful regions in images before applying color palettes. This approach will:
1. Identify specific objects/regions in the image (e.g., person, face, clothing, background)
2. Map palette colors semantically to appropriate regions
3. Apply color transformations with awareness of object boundaries
4. Better preserve textures and details within each region

## Model Selection

### Requirements
- **Low memory footprint**: Must run efficiently on standard server hardware
- **Fast inference time**: Processing should take less than 2 seconds per image
- **Reasonable accuracy**: Must identify key elements like people, clothing, backgrounds
- **Pre-trained availability**: Utilize existing models to avoid training from scratch

### Candidate Models

1. **MobileNetV3 + DeepLabV3**
   - Memory: ~20MB
   - Inference time: ~300ms on CPU
   - IoU score: ~72% on PASCAL VOC
   - Advantages: Very lightweight, good for server deployment
   - Supported by OpenCV's DNN module

2. **EfficientDet-Lite**
   - Memory: ~30MB
   - Inference time: ~500ms on CPU
   - IoU score: ~75% on COCO
   - Good balance of speed and accuracy

3. **MediaPipe's Selfie Segmentation**
   - Memory: ~5MB
   - Inference time: ~100ms on CPU
   - Limited to person/background segmentation
   - Extremely efficient but limited classes

### Recommended Model

**MobileNetV3 + DeepLabV3** with PASCAL VOC classes provides the best balance of efficiency and capability for our use case. It can identify people, clothing, and common background elements while maintaining reasonable inference speed.

## Implementation Approach

### 1. Segmentation Pipeline

```python
def segment_image(image):
    # Load pre-trained model
    net = cv2.dnn.readNetFromTensorflow('path/to/model.pb')
    
    # Prepare input blob
    blob = cv2.dnn.blobFromImage(image, 1.0/127.5, (513, 513), (127.5, 127.5, 127.5))
    net.setInput(blob)
    
    # Run inference
    output = net.forward()
    
    # Process and return segmentation masks
    return process_segmentation(output, image.shape)
```

### 2. Semantic Mapping Strategy

We'll define a mapping between segment classes and palette colors:

| Class ID | Class Name | Palette Color | Priority |
|----------|------------|---------------|----------|
| 15 | Person | - | - |
| 15.1 | Face/Skin | Neutral or Skin Tone | 1 |
| 15.2 | Clothing | Primary | 2 |
| 15.3 | Accessories | Accent | 3 |
| 1-14, 16-20 | Background/Objects | Background/Secondary | 4 |

For superhero images specifically, we'll create custom mappings:
- Cape/Cloak → Accent color
- Suit Body → Primary color
- Logo/Emblem → Secondary color
- Mask/Cowl → Primary or Accent color
- Utility Belt → Complementary color

### 3. Refinement Process

For each detected region:
1. Extract the segmentation mask
2. Apply color transfer preserving luminance and texture
3. Blend with edge-aware filtering to maintain details
4. Composite regions back together with priority handling

## Integration with Existing Code

### New Module Structure

```
backend/app/services/
├── image_processing.py (existing)
├── semantic_segmentation/
│   ├── __init__.py
│   ├── models.py        # Model loading and inference
│   ├── mappings.py      # Semantic-to-palette mappings
│   └── utils.py         # Helper functions
```

### Updates to Existing Code

The `apply_palette_with_masking_optimized` function in `image_processing.py` will be updated to optionally use semantic segmentation:

```python
def apply_palette_with_semantic_mapping(
    image_url: str, 
    palette_colors: List[str], 
    use_segmentation: bool = True
) -> bytes:
    # Load image
    # If use_segmentation:
    #   Call semantic segmentation
    #   Apply colors based on semantic mapping
    # Else:
    #   Fall back to current approach
```

## Implementation Phases

1. **Phase 1: Model Integration**
   - Add model loading and inference functionality
   - Create basic segmentation pipelines
   - Test with simple binary (foreground/background) segmentation

2. **Phase 2: Semantic Mappings**
   - Develop mapping strategies for different image types
   - Implement color transfer for each segment type
   - Add configurable mapping rules

3. **Phase 3: Integration & Optimization**
   - Integrate with existing palette application
   - Optimize for performance
   - Add fallback mechanisms for failure cases

## Memory and Performance Considerations

- Model files will be downloaded at build time and stored in the container
- Inference will use OpenCV's optimized DNN module for CPU inference
- For high traffic, consider:
  - Caching segmentation results
  - Downscaling images before segmentation, then upscaling masks
  - Async processing using FastAPI background tasks

## Expected Outcomes

- **Improved quality**: Colors applied with awareness of object boundaries
- **More realistic results**: Better texture preservation within segments
- **Semantic coherence**: Palette colors mapped appropriately to objects
- **Consistent performance**: Processing time under 2 seconds per image

## Fallback Mechanism

If segmentation fails or produces poor results (determined by confidence thresholds), the system will automatically fall back to the current dominant-color approach.

## Evaluation Metrics

1. Processing time (target: <2s)
2. Memory usage (target: <100MB)
3. User satisfaction ratings
4. A/B testing of old vs. new approach

## Next Steps

After implementation, future improvements could include:
- Fine-tuning models on our specific image domain
- Adding more specialized semantic classes for specific themes
- Implementing style transfer for even better texture preservation 