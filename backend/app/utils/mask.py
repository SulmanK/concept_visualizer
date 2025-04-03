"""
Masking utilities for sensitive data in logs.

This module provides utilities for masking sensitive information in logs,
such as session IDs, concept IDs, and storage paths.
"""

import logging
import re
from typing import Optional

# Configure logging
logger = logging.getLogger(__name__)

def mask_id(id_value: Optional[str], visible_chars: int = 8) -> str:
    """Mask an ID (session ID, concept ID, etc.) to protect privacy in logs.
    
    Args:
        id_value: The ID to mask
        visible_chars: Number of characters to show before masking
        
    Returns:
        Masked ID showing only the first few characters followed by asterisks
    """
    if not id_value:
        return "unknown"
        
    if len(id_value) <= visible_chars:
        return f"{id_value}***"
        
    return f"{id_value[:visible_chars]}***"

def mask_path(path: Optional[str]) -> str:
    """Mask a storage path to protect session ID privacy.
    
    Args:
        path: Storage path potentially containing session ID
        
    Returns:
        Masked path with session ID portion obscured
    """
    if not path or "/" not in path:
        return path or "empty-path"
        
    # Split path at first slash to separate session ID from filename
    parts = path.split("/", 1)
    if len(parts) >= 2:
        session_part = parts[0]
        file_part = parts[1]
        return f"{mask_id(session_part)}/{file_part}"
    
    return path

def mask_ip(ip_address: Optional[str]) -> str:
    """Mask an IP address to protect privacy in logs.
    
    Args:
        ip_address: The IP address to mask
        
    Returns:
        Masked IP address showing only parts of the address
    """
    if not ip_address:
        return "unknown-ip"
    
    # Check if IPv4
    ipv4_pattern = r'^(\d+)\.(\d+)\.(\d+)\.(\d+)$'
    ipv4_match = re.match(ipv4_pattern, ip_address)
    if ipv4_match:
        return f"{ipv4_match.group(1)}.{ipv4_match.group(2)}.*.*"
    
    # Check if IPv6
    if ':' in ip_address:
        parts = ip_address.split(':')
        visible_parts = parts[:2]
        return f"{':'.join(visible_parts)}:****"
    
    # Unknown format, mask most of it
    if len(ip_address) > 4:
        return f"{ip_address[:4]}****"
    
    return "masked-ip"

def mask_redis_key(key: Optional[str]) -> str:
    """Mask a Redis key that might contain sensitive information.
    
    Args:
        key: Redis key to mask
        
    Returns:
        Masked Redis key with sensitive parts obscured
    """
    if not key:
        return "unknown-key"
    
    # Handle session keys
    if key.startswith("session:"):
        parts = key.split(":", 1)
        if len(parts) > 1:
            return f"session:{mask_id(parts[1])}"
    
    # Handle rate limit keys
    if "rate-limit" in key and ":" in key:
        parts = key.split(":")
        # Try to identify and mask the identifier part (session ID or IP)
        if len(parts) >= 3:
            masked_parts = parts[:2]  # Keep the prefix parts
            identifier = parts[2]  # This is typically the session ID or IP
            masked_parts.append(mask_id(identifier))
            if len(parts) > 3:
                masked_parts.extend(parts[3:])  # Keep any suffix parts
            return ":".join(masked_parts)
    
    # Generic masking for other keys
    if ":" in key:
        parts = key.split(":")
        if len(parts) >= 2 and len(parts[-1]) > 8:
            parts[-1] = mask_id(parts[-1])
            return ":".join(parts)
    
    # Default case - if we don't recognize the format, return as is
    return key 