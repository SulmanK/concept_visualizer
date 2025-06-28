# Cloud Run Performance Optimizations

## Executive Summary

This document outlines comprehensive performance optimizations for the Cloud Run worker function beyond the current semaphore-based concurrency control implemented in [cloud-run-timeout-fix.md](cloud-run-timeout-fix.md). These optimizations target multiple bottlenecks in the image processing pipeline to achieve sub-3-minute execution times consistently.

## Current Performance Baseline

**After Semaphore Fix:**

- **Execution Time**: 3-4 minutes for 7 palette variations
- **Resource Usage**: 1 CPU, 2GB RAM, controlled concurrency
- **Bottlenecks Identified**:
  1. Image processing algorithms (K-means clustering taking ~30-45 seconds per palette)
  2. Memory usage patterns during concurrent operations (peaks at ~1.8GB)
  3. Storage upload bandwidth and latency (~10-15 seconds per image upload)
  4. Cold start initialization overhead (~5-10 seconds)

## Optimization Categories

### 1. Image Processing Algorithm Optimizations

#### Problem: K-means Clustering Performance

The `apply_palette_with_masking_optimized` function performs expensive K-means clustering on full-resolution images, which can be 2048x2048 pixels or larger. This results in:

- ~30-45 seconds per palette application
- High memory consumption (arrays of millions of pixels)
- CPU-intensive operations on single core

#### Solution: Smart Downsampling Strategy

```python
def apply_palette_with_masking_optimized_v2(image: np.ndarray, palette: List[Tuple[int, int, int]], k: int = 10) -> np.ndarray:
    """Optimized palette application with smart downsampling."""
    height, width = image.shape[:2]

    # 1. Downsample for clustering analysis if image is large
    if width > 1024 or height > 1024:
        scale = min(1024 / width, 1024 / height)
        sample_width = int(width * scale)
        sample_height = int(height * scale)
        sample_image = cv2.resize(image, (sample_width, sample_height), interpolation=cv2.INTER_AREA)
    else:
        sample_image = image

    # 2. Perform K-means on downsampled image (faster)
    lab_sample = cv2.cvtColor(sample_image.astype(np.uint8), cv2.COLOR_BGR2LAB)
    pixels = lab_sample.reshape(-1, 3).astype(np.float32)

    # 3. Use fewer iterations for faster convergence
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 50, 0.2)  # Reduced from 100, 0.1
    _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 5, cv2.KMEANS_RANDOM_CENTERS)  # Reduced from 10

    # 4. Apply results to full resolution using efficient mapping
    return apply_clustering_to_full_image(image, sample_image, centers, labels, palette)
```

**Expected Impact**: 60-75% reduction in processing time per palette (from 30-45s to 8-12s).

### 2. Memory Management Optimizations

#### Problem: Memory Spikes During Concurrent Processing

Current implementation can spike to 1.8GB when processing multiple palettes concurrently.

#### Solution: Intelligent Memory Management

```python
class MemoryAwareProcessor:
    def __init__(self):
        self.memory_threshold = 1500  # MB
        self.processing_semaphore = asyncio.Semaphore(2)  # Adaptive based on memory

    async def process_palette_with_memory_control(self, image_data: bytes, palette: Dict) -> bytes:
        # Check memory before processing
        current_memory = psutil.Process().memory_info().rss / 1024 / 1024

        if current_memory > self.memory_threshold:
            # Trigger garbage collection
            gc.collect()
            await asyncio.sleep(0.1)  # Brief pause for cleanup

        async with self.processing_semaphore:
            try:
                return await self._process_single_palette_optimized(image_data, palette)
            finally:
                # Explicit cleanup after each palette
                gc.collect()
```

### 3. Storage Upload Optimizations

#### Problem: Sequential Upload Bottleneck

Current uploads take 10-15 seconds each due to:

- Large image file sizes (1-3MB PNG files)
- No connection reuse
- No compression optimization

#### Solution: Optimized Upload Pipeline

```python
class OptimizedUploader:
    def __init__(self):
        self.session = None  # Persistent HTTP session
        self.upload_semaphore = asyncio.Semaphore(3)  # Concurrent uploads

    async def upload_batch_optimized(self, variations: List[Dict]) -> List[Dict]:
        # 1. Pre-compress all images
        compressed_variations = await self._compress_images_batch(variations)

        # 2. Upload concurrently with connection reuse
        async with self._get_persistent_session() as session:
            upload_tasks = [
                self._upload_single_optimized(session, var)
                for var in compressed_variations
            ]
            return await asyncio.gather(*upload_tasks, return_exceptions=True)

    async def _compress_images_batch(self, variations: List[Dict]) -> List[Dict]:
        """Compress images for faster upload."""
        for variation in variations:
            # Convert PNG to optimized JPEG for upload (PNG for storage)
            original_size = len(variation['image_data'])
            if original_size > 500 * 1024:  # 500KB threshold
                compressed = await self._compress_for_upload(variation['image_data'])
                variation['upload_data'] = compressed
                variation['original_data'] = variation['image_data']  # Keep original for storage
        return variations
```

**Expected Impact**: 40-50% reduction in upload time (from 10-15s to 5-8s per image).

### 4. Pre-processing and Caching Optimizations

#### Problem: Redundant Image Processing

Base image is processed repeatedly for validation and format conversion.

#### Solution: Smart Pre-processing

```python
class ImagePreprocessor:
    def __init__(self):
        self._preprocessed_cache = {}

    async def preprocess_base_image_once(self, image_data: bytes) -> Dict:
        """Preprocess base image once for all palette variations."""
        cache_key = hashlib.md5(image_data).hexdigest()

        if cache_key in self._preprocessed_cache:
            return self._preprocessed_cache[cache_key]

        # Single preprocessing for all variations
        img = PILImage.open(BytesIO(image_data))

        # Standardize format
        if img.mode != "RGB":
            img = img.convert("RGB")

        # Optimize size (configurable max dimension)
        max_dim = 1500
        if max(img.width, img.height) > max_dim:
            img.thumbnail((max_dim, max_dim), PILImage.Resampling.LANCZOS)

        # Pre-convert to arrays needed for processing
        processed = {
            'pil_image': img,
            'bgr_array': cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR),
            'dimensions': (img.width, img.height),
            'optimized_bytes': self._to_optimized_bytes(img)
        }

        self._preprocessed_cache[cache_key] = processed
        return processed
```

### 5. Configuration-Based Performance Tuning

#### New Environment Variables for Optimization Control

```bash
# Image processing optimizations
CONCEPT_IMAGE_MAX_DIMENSION=1500
CONCEPT_KMEANS_MAX_ITERATIONS=50
CONCEPT_CLUSTERING_SAMPLE_SIZE=1024
CONCEPT_COMPRESSION_QUALITY=85

# Memory management
CONCEPT_MEMORY_CLEANUP_THRESHOLD_MB=1500
CONCEPT_GARBAGE_COLLECTION_INTERVAL=3

# Upload optimizations
CONCEPT_UPLOAD_COMPRESSION_ENABLED=true
CONCEPT_UPLOAD_MAX_SIZE_KB=500
CONCEPT_CONNECTION_POOL_SIZE=5
CONCEPT_UPLOAD_TIMEOUT_SECONDS=30
```

## Implementation Priority and Timeline

### Phase 1: Quick Wins (Week 1)

1. **Image compression for uploads** - Easy implementation, 40% upload time reduction
2. **Memory cleanup optimization** - Simple gc.collect() calls, stability improvement
3. **Pre-processing caching** - Moderate implementation, 25% overall time reduction

### Phase 2: Algorithm Optimization (Week 2)

1. **K-means clustering optimization** - Moderate complexity, 60% processing time reduction
2. **Connection pooling for uploads** - Easy implementation, 20% upload time reduction

### Phase 3: Advanced Optimizations (Week 3)

1. **Adaptive concurrency based on memory** - Complex implementation, stability improvement
2. **Smart image downsampling** - Complex implementation, additional processing improvement

## Expected Performance Improvements

### After Phase 1 (Quick Wins)

- **Total execution time**: 2.5-3 minutes (from 3-4 minutes)
- **Memory usage**: More stable, fewer spikes
- **Upload time**: 6-8 seconds per image (from 10-15 seconds)

### After Phase 2 (Algorithm Optimization)

- **Total execution time**: 1.5-2 minutes
- **Processing time per palette**: 8-12 seconds (from 30-45 seconds)
- **Memory usage**: 15-20% reduction

### After Phase 3 (Complete)

- **Total execution time**: 1-1.5 minutes consistently
- **Success rate**: >99% (from ~95%)
- **Resource efficiency**: 40% better CPU/memory utilization

## Monitoring and Success Metrics

### Key Performance Indicators

1. **End-to-end execution time**: Target <2 minutes
2. **Individual palette processing time**: Target <15 seconds
3. **Memory peak usage**: Target <1.5GB
4. **Upload success rate**: Target >99%
5. **Error rate**: Target <2%

### Monitoring Implementation

```python
class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}

    async def track_palette_processing(self, palette_name: str):
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.logger.info(f"Palette {palette_name} processed in {duration:.2f}s")

    async def track_memory_usage(self):
        memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
        self.logger.info(f"Memory usage: {memory_mb:.1f}MB")
        return memory_mb
```

## Risk Assessment and Mitigation

### Risks

1. **Image quality degradation** from compression/downsampling
2. **Memory leaks** from caching strategies
3. **Complexity increase** making debugging harder

### Mitigation Strategies

1. **Quality validation**: Automated tests comparing output images
2. **Memory monitoring**: Alerts when usage exceeds thresholds
3. **Feature flags**: Ability to disable optimizations if issues arise
4. **Gradual rollout**: Test with small percentage of traffic first

## Conclusion

These optimizations target the major bottlenecks in Cloud Run function execution while maintaining image quality and system reliability. The phased approach allows for incremental improvements with measurable results at each stage.

**Target Outcome**: Consistent sub-2-minute execution times with improved stability and resource efficiency.
