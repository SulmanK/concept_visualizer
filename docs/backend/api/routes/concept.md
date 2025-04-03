# Concept Generation and Refinement API

This document describes the concept generation and refinement endpoints in the Concept Visualizer API.

## Overview

The concept generation and refinement API provides the core functionality of the application:
- Generating visual concepts based on user input
- Refining existing concepts based on feedback
- Providing variations of existing concepts

## Endpoints

### Generate Concept

```
POST /api/concept/generate
```

Generates a new visual concept based on a text prompt.

#### Request Body

```json
{
  "logo_description": "A modern technology company logo with blue and green colors",
  "theme_description": "Clean, professional, tech-oriented",
  "additional_prompt": "Include a circuit board motif",
  "n_outputs": 1
}
```

Parameters:
- `logo_description`: Text description of the logo (required)
- `theme_description`: Description of the theme/style (required)
- `additional_prompt`: Optional additional instructions (optional)
- `n_outputs`: Number of concepts to generate (default: 1, max: 3)

#### Response

```json
{
  "concepts": [
    {
      "image_b64": "base64-encoded-image-data",
      "color_palette": ["#1A2B3C", "#DEFABC", "#456789"],
      "prompt": "Generated prompt used for this concept",
      "metadata": {
        "model_used": "JigsawStack model info",
        "generation_time": "2023-04-01T12:34:56Z"
      }
    }
  ],
  "session_id": "user-session-id"
}
```

### Generate With Palettes

```
POST /api/concept/generate-with-palettes
```

Generates a concept with pre-generated color palettes.

#### Request Body

```json
{
  "logo_description": "A modern technology company logo",
  "theme_description": "Clean, professional, tech-oriented",
  "additional_prompt": "Include a circuit board motif",
  "color_palettes": [
    ["#1A2B3C", "#DEFABC", "#456789"],
    ["#FFFFFF", "#000000", "#FF0000"]
  ]
}
```

Parameters:
- `logo_description`: Text description of the logo (required)
- `theme_description`: Description of the theme/style (required)
- `additional_prompt`: Optional additional instructions (optional)
- `color_palettes`: List of color palettes to use (required)

#### Response

Same as the generate endpoint.

### Refine Concept

```
POST /api/concept/refine
```

Refines an existing concept based on feedback.

#### Request Body

```json
{
  "original_concept": {
    "image_b64": "base64-encoded-image-data",
    "color_palette": ["#1A2B3C", "#DEFABC", "#456789"],
    "prompt": "Original prompt"
  },
  "refinement_prompt": "Make the logo more abstract and use brighter colors",
  "keep_colors": false,
  "aspect": "overall"
}
```

Parameters:
- `original_concept`: The concept to refine (required)
- `refinement_prompt`: Instructions for refinement (required)
- `keep_colors`: Whether to keep the original color palette (default: false)
- `aspect`: What aspect to refine - "overall", "colors", "style", "layout" (default: "overall")

#### Response

```json
{
  "refined_concept": {
    "image_b64": "base64-encoded-image-data",
    "color_palette": ["#1A2B3C", "#DEFABC", "#456789"],
    "prompt": "Refined prompt used for this concept",
    "metadata": {
      "model_used": "JigsawStack model info",
      "generation_time": "2023-04-01T12:34:56Z",
      "original_concept_id": "original-concept-id"
    }
  },
  "session_id": "user-session-id"
}
```

## Implementation Details

### Generation Process

1. Validate input parameters
2. Apply rate limiting for the session
3. Create a prompt for the JigsawStack API
4. Generate the concept using the JigsawStack client
5. Extract and process the color palette
6. Return the generated concept

### Refinement Process

1. Validate input parameters
2. Apply rate limiting for the session
3. Create a refinement prompt based on the original concept and feedback
4. Generate the refined concept using the JigsawStack client
5. Update the color palette if needed
6. Return the refined concept

### Rate Limiting

The concept generation and refinement endpoints are rate-limited:
- Generation: 10 requests per month per session
- Refinement: 10 requests per hour per session

### Error Handling

Common errors:

| Status Code | Error Code | Description |
|-------------|------------|-------------|
| 400 | validation_error | Invalid request parameters |
| 429 | rate_limit_exceeded | Rate limit exceeded |
| 503 | service_unavailable | Image generation service unavailable |

## Best Practices

1. **Provide Clear Descriptions**: The more specific and detailed the descriptions, the better the results
2. **Use Appropriate Refinement Aspects**: Choose the aspect that best matches what you want to refine
3. **Batch Requests When Possible**: Use n_outputs parameter to generate multiple concepts in one request
4. **Implement Client-Side Rate Limiting**: To avoid hitting server-side limits 