# Validation Utilities

This directory will contain input validation utilities for the Concept Visualizer API.

## Overview

The `validation` utilities module is intended to provide functions for validating input data beyond what Pydantic models offer. While currently a placeholder for future functionality, it will centralize complex validation logic that can be reused across the application.

## Planned Functionality

The following functionalities are planned for this module:

1. **Custom Validators**
   - Complex business rule validation
   - Cross-field validation functions
   - Contextual validation (validation that depends on application state)

2. **Sanitization**
   - Input sanitization for security
   - Data cleaning utilities
   - Normalization functions

3. **Extended Validation**
   - Format validation (beyond regex patterns)
   - Semantic validation
   - Domain-specific validation rules

## Usage Guidelines

When adding validation utilities to this module:

1. Make validators composable where possible
2. Provide clear error messages that guide users on how to fix issues
3. Document validation rules clearly in function docstrings
4. Ensure validators are unit tested with both valid and invalid inputs
5. Consider performance implications for validation of large inputs

## Integration with Pydantic

This module is designed to complement Pydantic's validation capabilities:

- Pydantic handles basic type validation, required fields, and simple constraints
- This module will handle more complex validation logic that can't be easily expressed in Pydantic models

## Related Modules

- `app.models`: Pydantic models that define data structures
- `app.utils.data`: For data transformation utilities
- `app.core.exceptions`: For custom validation exceptions

## Example (Future Implementation)

```python
# Example of a validation utility that might be added in the future

from typing import Dict, Any, List, Optional
import re

def validate_prompt_content(
    prompt: str, 
    min_length: int = 10, 
    max_length: int = 1000,
    disallowed_patterns: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Validate a concept generation prompt for compliance with content guidelines.
    
    Args:
        prompt: The text prompt to validate
        min_length: Minimum acceptable length
        max_length: Maximum acceptable length
        disallowed_patterns: List of regex patterns for content that is not allowed
        
    Returns:
        Dictionary with validation result:
          - valid: Boolean indicating if the prompt is valid
          - errors: List of error messages (empty if valid)
          
    Example:
        >>> validate_prompt_content("Generate a logo", min_length=20)
        {"valid": False, "errors": ["Prompt too short, minimum length is 20 characters"]}
    """
    errors = []
    
    # Length validation
    if len(prompt) < min_length:
        errors.append(f"Prompt too short, minimum length is {min_length} characters")
    
    if len(prompt) > max_length:
        errors.append(f"Prompt too long, maximum length is {max_length} characters")
    
    # Content validation
    if disallowed_patterns:
        for pattern in disallowed_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                errors.append(f"Prompt contains disallowed content matching pattern: {pattern}")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }
``` 