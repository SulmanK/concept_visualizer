# Security Masking Utilities

The `mask.py` module provides utilities for masking sensitive information in logs and error messages within the Concept Visualizer API.

## Overview

This module helps protect personally identifiable information (PII) and sensitive data by:

1. Masking user IDs, session IDs, and other identifiers
2. Hiding sensitive parts of paths and URLs
3. Obfuscating API keys and tokens
4. Implementing consistent masking patterns across the application

## Key Functions

### User ID Masking

```python
def mask_id(id_value: Optional[str], keep_prefix: bool = True) -> str:
    """
    Mask a user ID or other identifier.

    Args:
        id_value: The ID to mask
        keep_prefix: Whether to keep the prefix (e.g., "user-") visible

    Returns:
        Masked ID (e.g., "user-***567" from "user-123567")
    """
    # Implementation...
```

This function masks most of an ID while preserving enough information for debugging:

- Original: `user-123456789`
- Masked: `user-******789`

### Path Masking

```python
def mask_path(path: Optional[str]) -> str:
    """
    Mask sensitive parts of a path.

    Args:
        path: The path to mask

    Returns:
        Path with sensitive parts masked
    """
    # Implementation...
```

This function masks user IDs and other sensitive information in paths:

- Original: `/users/123456789/images/profile.png`
- Masked: `/users/******789/images/profile.png`

### URL Masking

```python
def mask_url(url: Optional[str]) -> str:
    """
    Mask sensitive parts of a URL.

    Args:
        url: The URL to mask

    Returns:
        URL with sensitive parts masked
    """
    # Implementation...
```

This function masks sensitive parts in URLs, including tokens and IDs:

- Original: `https://api.example.com/users/123456789?token=abcdef1234`
- Masked: `https://api.example.com/users/******789?token=******1234`

### API Key Masking

```python
def mask_api_key(api_key: Optional[str]) -> str:
    """
    Mask an API key or token.

    Args:
        api_key: The key to mask

    Returns:
        Masked API key (e.g., "******ef34" from "abcdef34")
    """
    # Implementation...
```

This function masks most of an API key while preserving the last few characters:

- Original: `sk_live_abcdefghijklmnopqrstuvwxyz`
- Masked: `sk_live_************************wxyz`

### Email Masking

```python
def mask_email(email: Optional[str]) -> str:
    """
    Mask an email address.

    Args:
        email: The email to mask

    Returns:
        Email with local part masked (e.g., "j**@example.com" from "john@example.com")
    """
    # Implementation...
```

This function masks most of the local part of an email address:

- Original: `john.doe@example.com`
- Masked: `j******.d**@example.com`

## Usage Examples

### Masking User IDs in Logs

```python
import logging
from app.utils.security.mask import mask_id

logger = logging.getLogger(__name__)

def process_user_data(user_id: str, data: dict):
    # Mask the user ID in logs
    masked_user_id = mask_id(user_id)

    logger.info(f"Processing data for user {masked_user_id}")

    # Process the data...

    logger.info(f"Completed processing for user {masked_user_id}")
```

### Masking Paths in Storage Operations

```python
from app.utils.security.mask import mask_path

def upload_user_file(user_id: str, file_path: str, content: bytes):
    # Create the storage path
    storage_path = f"users/{user_id}/{file_path}"

    # Mask the path for logging
    masked_path = mask_path(storage_path)

    logger.info(f"Uploading file to {masked_path}")

    # Upload the file...

    logger.info(f"Successfully uploaded file to {masked_path}")
```

### Masking Multiple Types of Data

```python
from app.utils.security.mask import mask_id, mask_email, mask_api_key

def create_user_account(email: str, api_key: str):
    # Mask sensitive data for logging
    masked_email = mask_email(email)
    masked_api_key = mask_api_key(api_key)

    logger.info(f"Creating account for {masked_email} with API key {masked_api_key}")

    # Create the account...
    user_id = "user-123456789"

    # Mask the new user ID
    masked_user_id = mask_id(user_id)

    logger.info(f"Created account for {masked_email}, assigned ID {masked_user_id}")

    return user_id
```

## Implementation Details

### Masking Patterns

The module uses consistent masking patterns:

1. **IDs**: Replace middle part with asterisks
2. **Emails**: Preserve first character and domain, mask the rest
3. **API Keys**: Show only last few characters
4. **Paths**: Mask IDs within paths but keep structure visible

### Default Behavior

The module handles edge cases gracefully:

- `None` values are returned as `"None"`
- Empty strings are returned as `""`
- Short strings are masked with minimal characters shown

### Regular Expressions

The module uses regular expressions for precise masking:

```python
# Example: Extract and mask user IDs in paths
def mask_path(path: Optional[str]) -> str:
    if not path:
        return str(path)

    # Pattern to identify user IDs in paths
    pattern = r'(/|^)(user-|users/|user/)([a-zA-Z0-9-]+)'

    # Replace with masked version
    return re.sub(pattern, lambda m: f"{m.group(1)}{m.group(2)}{mask_id(m.group(3), False)}", path)
```

## Security Considerations

### Log Security

The masking functions help prevent sensitive data exposure in:

1. Application logs
2. Error reports
3. Monitoring systems
4. Debug output

### PII Protection

The module helps comply with data protection regulations by masking:

1. User identifiers
2. Email addresses
3. Session identifiers
4. Other potentially identifying information

### Configuration Options

In some cases, masking behavior can be configured:

```python
# Configure ID masking to show or hide prefixes
masked_id = mask_id(user_id, keep_prefix=True)  # "user-******789"
masked_id = mask_id(user_id, keep_prefix=False) # "******789"
```

## Related Documentation

- [Logging Setup](../logging/setup.md): Configuration of logging with masked data
- [JWT Utilities](../jwt_utils.md): Authentication utilities that mask sensitive data
- [Image Persistence Service](../../services/persistence/image_persistence_service.md): Uses masking for storage paths
- [Error Handling](../../core/exceptions.md): Error handling with masked sensitive data
