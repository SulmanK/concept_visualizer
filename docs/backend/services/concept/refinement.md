# Concept Refinement Service

The `refinement.py` module provides specialized functionality for refining and iteratively improving existing visual concepts.

## Overview

The concept refinement service enables:

1. Iterative improvement of previously generated visual concepts
2. Processing of user feedback to enhance designs
3. Generation of multiple design variations based on an original concept
4. Comparison between original and refined concepts

This service is crucial for implementing an iterative design workflow, allowing users to progressively refine their concepts until they achieve the desired result.

## Key Components

### ConceptRefiner

```python
class ConceptRefiner:
    """Service for refining existing visual concepts."""
    
    def __init__(
        self, 
        client: JigsawStackClient,
        persistence_service: ConceptPersistenceServiceInterface
    ):
        """Initialize the concept refiner with required dependencies."""
        self.client = client
        self.persistence_service = persistence_service
        self.logger = logging.getLogger("concept_service.refiner")
```

The ConceptRefiner is responsible for improving existing concepts by applying refinement prompts and generating variations.

## Core Functionality

### Refine Concept

```python
async def refine_concept(
    self, concept_id: str, refinement_prompt: str
) -> RefinementResponse:
    """Refine an existing concept based on refinement instructions."""
```

This method applies refinement instructions to an existing concept to create an improved version.

**Parameters:**
- `concept_id`: ID of the concept to refine
- `refinement_prompt`: Textual instructions for refining the concept

**Returns:**
- `RefinementResponse`: Contains the refined image URL, original image URL, and metadata

**Raises:**
- `ResourceNotFoundError`: If the concept with the given ID doesn't exist
- `RefinementError`: If the refinement process fails
- `ServiceUnavailableError`: If external services are unavailable

### Generate Variations

```python
async def generate_variations(
    self, concept_id: str, variation_count: int = 3
) -> List[ConceptVariation]:
    """Generate multiple variations of an existing concept."""
```

This method creates multiple alternative versions of an existing concept.

**Parameters:**
- `concept_id`: ID of the base concept to create variations from
- `variation_count`: Number of variations to generate (default: 3)

**Returns:**
- List of `ConceptVariation` objects, each containing a variation image and metadata

**Raises:**
- `ResourceNotFoundError`: If the base concept doesn't exist
- `VariationGenerationError`: If the variation generation fails

### Process Refinement Prompt

```python
def process_refinement_prompt(
    self, original_concept: Concept, refinement_prompt: str
) -> str:
    """Process a refinement prompt to optimize the refinement outcome."""
```

This method enhances raw refinement instructions to improve the refinement results.

**Parameters:**
- `original_concept`: The base concept being refined
- `refinement_prompt`: Original refinement instructions from the user

**Returns:**
- Enhanced refinement prompt optimized for the AI service

## Refinement Flow

The refinement process follows these steps:

1. **Concept Retrieval**: Fetch the original concept from the persistence service
2. **Prompt Enhancement**: Process and enhance the refinement instructions
3. **Refinement Request**: Send the original image and enhanced prompt to the AI service
4. **Result Processing**: Process the refinement result and create response objects
5. **Optional Persistence**: Store the refined concept if requested

## Integration with Other Services

The refinement service integrates with:

1. **JigsawStack API**: For AI-powered refinement processing
2. **Concept Persistence Service**: For retrieving and storing concepts
3. **Image Processing Service**: For image manipulation and comparison

## Usage Examples

### Refining a Concept

```python
from app.services.concept.refinement import ConceptRefiner
from app.services.jigsawstack.client import JigsawStackClient
from app.services.persistence.concept_persistence_service import ConceptPersistenceService

# Create dependencies
client = JigsawStackClient(api_key="your_api_key")
persistence_service = ConceptPersistenceService(...)

# Initialize the refiner
refiner = ConceptRefiner(client, persistence_service)

# Refine a concept
result = await refiner.refine_concept(
    concept_id="abc123",
    refinement_prompt="Make the logo more minimalist and use a brighter blue color"
)

# Access the refinement result
original_url = result.original_image_url
refined_url = result.refined_image_url
refinement_id = result.refinement_id
```

### Generating Variations

```python
# Generate variations of a concept
variations = await refiner.generate_variations(
    concept_id="abc123",
    variation_count=5
)

# Process the variations
for i, variation in enumerate(variations):
    print(f"Variation {i+1}: {variation.image_url}")
    print(f"Difference score: {variation.difference_score}")
```

## Error Handling

The refinement service implements comprehensive error handling:

1. **Resource Errors**: When requested concepts don't exist
2. **Service Errors**: When external services fail or are unavailable
3. **Validation Errors**: When inputs don't meet requirements
4. **Processing Errors**: When refinement processing fails

## Performance Considerations

- Refinement operations are performed asynchronously
- Image data is efficiently managed to minimize memory usage
- Requests to external services are optimized for performance
- Caching is used where appropriate to avoid redundant operations

## Related Documentation

- [Concept Service](service.md): Main concept service that uses the refiner
- [Concept Generation](generation.md): Details on initial concept generation
- [Persistence Service](../persistence/concept_persistence_service.md): Storage service for concepts
- [JigsawStack Client](../jigsawstack/client.md): Client for the external AI service
- [Refinement API Routes](../../api/routes/concept/refinement.md): API routes that use this service 