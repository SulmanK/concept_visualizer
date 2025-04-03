"""
Health API utilities.

This module provides utility functions for health check and rate limit endpoints.
"""

import calendar
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger(__name__)


def get_reset_time(period: str) -> int:
    """Calculate approximate reset time in seconds.
    
    Args:
        period: The period string (minute, hour, day, month)
        
    Returns:
        int: Approximate seconds until reset
    """
    now = datetime.now()
    
    if period == "minute":
        # Reset at the next minute
        return 60 - now.second
    elif period == "hour":
        # Reset at the next hour
        return (60 - now.minute) * 60 - now.second
    elif period == "day":
        # Reset at midnight
        seconds_in_day = 24 * 60 * 60
        seconds_passed = now.hour * 3600 + now.minute * 60 + now.second
        return seconds_in_day - seconds_passed
    elif period == "month":
        # Reset at the 1st of next month (very approximate)
        days_in_month = calendar.monthrange(now.year, now.month)[1]
        days_left = days_in_month - now.day
        return days_left * 24 * 60 * 60 + (24 - now.hour) * 60 * 60


def mask_ip(ip_address: str) -> str:
    """Mask an IP address for privacy in logs.
    
    Args:
        ip_address: The IP address to mask
        
    Returns:
        str: Masked IP address
    """
    if not ip_address:
        return "unknown"
    
    # For IPv4 addresses
    if '.' in ip_address:
        parts = ip_address.split('.')
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.**.**"
    
    # For IPv6 addresses
    if ':' in ip_address:
        return ip_address.split(':')[0] + ':****:****'
    
    # If not a recognized format, mask most of it
    if len(ip_address) > 4:
        return ip_address[:4] + '*' * (len(ip_address) - 4)
    
    return "****"


def mask_id(id_value: str) -> str:
    """Mask an identifier (session ID or IP) for privacy in logs.
    
    Args:
        id_value: The identifier to mask
        
    Returns:
        str: Masked identifier
    """
    if not id_value:
        return "unknown"
        
    # Check if this is a session ID or IP format
    if id_value.startswith("session:"):
        # Extract and mask the session ID part
        session_id = id_value[8:]
        if len(session_id) <= 4:
            return "session:[ID_TOO_SHORT]"
        return f"session:{session_id[:4]}{'*' * (len(session_id) - 4)}"
    elif id_value.startswith("ip:"):
        # Extract and mask the IP part
        ip = id_value[3:]
        masked_ip = mask_ip(ip)
        return f"ip:{masked_ip}"
    
    # Default masking for other formats
    if len(id_value) > 4:
        return id_value[:4] + '*' * (len(id_value) - 4)
    
    return "****"


def mask_key(key: str) -> str:
    """Mask a Redis key that might contain sensitive information.
    
    Args:
        key: The Redis key to mask
        
    Returns:
        str: Masked Redis key
    """
    if not key:
        return "unknown"
    
    # Check if key is in format "session:{session_id}:..."
    if "session:" in key:
        parts = key.split(":")
        for i, part in enumerate(parts):
            if i > 0 and parts[i-1] == "session" and len(part) > 4:
                # This part is likely a session ID
                parts[i] = part[:4] + '*' * (len(part) - 4)
    
    # If key contains an IP address, mask it
    else:
        parts = key.split(':')
        masked_parts = []
        
        for part in parts:
            if '.' in part and len(part.split('.')) == 4:
                # Likely an IPv4 address
                masked_parts.append(mask_ip(part))
            else:
                masked_parts.append(part)
        
        return ':'.join(masked_parts)
    
    return ':'.join(parts) 