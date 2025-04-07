"""
Masking utilities.

This module provides functions for masking sensitive data for logging,
such as user IDs, concept IDs, and storage paths.
"""

import logging
import re
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)


def mask_id(id_string: str, visible_chars: int = 4) -> str:
    """Mask an ID (user ID, concept ID, etc.) to protect privacy in logs.
    
    Args:
        id_string: ID string to mask
        visible_chars: Number of characters to leave visible at start
        
    Returns:
        Masked ID with only the first few characters visible
    """
    if not id_string:
        return "none"
        
    if len(id_string) <= visible_chars:
        return id_string
        
    return id_string[:visible_chars] + "****"


def mask_path(path: str) -> str:
    """Mask a storage path to protect user ID privacy.
    
    Args:
        path: Storage path potentially containing user ID
        
    Returns:
        Masked path with user ID portion obscured
    """
    if not path:
        return "none"
        
    # Split path at first slash to separate user ID from filename
    parts = path.split("/", 1)
    if len(parts) < 2:
        return mask_id(path)
        
    user_part = parts[0]
    file_part = parts[1]
    
    return f"{mask_id(user_part)}/{file_part}"


def mask_ip(ip_address: str) -> str:
    """Mask an IP address to protect privacy in logs.
    
    Args:
        ip_address: IP address to mask
        
    Returns:
        Masked IP address with last part obscured
    """
    if not ip_address:
        return "none"
        
    if ":" in ip_address:  # IPv6
        parts = ip_address.split(":")
        masked_parts = parts[:-2] + ["****"]
        return ":".join(masked_parts)
    else:  # IPv4
        parts = ip_address.split(".")
        masked_parts = parts[:-1] + ["***"]
        return ".".join(masked_parts)


def mask_url(url: str) -> str:
    """Mask a URL to remove sensitive query parameters.
    
    Args:
        url: URL to mask
        
    Returns:
        URL with sensitive query parameters masked
    """
    if not url:
        return "none"
        
    # List of sensitive parameter names to mask
    sensitive_params = ["token", "key", "secret", "password", "auth"]
    
    # Check if URL has query parameters
    if "?" not in url:
        return url
        
    base_url, query = url.split("?", 1)
    
    # Process each query parameter
    params = query.split("&")
    masked_params = []
    
    for param in params:
        if "=" in param:
            name, value = param.split("=", 1)
            if any(p in name.lower() for p in sensitive_params):
                masked_params.append(f"{name}=****")
            else:
                masked_params.append(param)
        else:
            masked_params.append(param)
            
    return f"{base_url}?{'&'.join(masked_params)}"


def mask_key(key: str) -> str:
    """Mask a Redis key or similar identifier for logging.
    
    Args:
        key: Redis key to mask
        
    Returns:
        Masked key with sensitive parts obscured
    """
    if not key:
        return "none"
        
    # Handle user keys
    if key.startswith("user:"):
        parts = key.split(":", 2)
        if len(parts) > 1:
            return f"user:{mask_id(parts[1])}"
            
    # Handle IP keys
    if key.startswith("ip:"):
        parts = key.split(":", 2)
        if len(parts) > 1:
            return f"ip:{mask_ip(parts[1])}"
            
    # Try to identify and mask the identifier part (user ID or IP)
    if ":" in key:
        parts = key.split(":")
        if len(parts) > 2:
            identifier = parts[2]  # This is typically the user ID or IP
            masked_id = mask_id(identifier)
            parts[2] = masked_id
            return ":".join(parts)
            
    # Default case - generic masking
    return re.sub(r'([a-f0-9]{8})[a-f0-9]*', r'\1****', key) 