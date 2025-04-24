#!/usr/bin/env python
"""Security utilities for masking sensitive information.

This module provides functions to mask various types of sensitive information
such as credit card numbers, email addresses, and phone numbers.
"""

import logging
import re
from typing import Optional

# Configure module logger
logger = logging.getLogger(__name__)


def mask_credit_card(card_number: Optional[str]) -> Optional[str]:
    """Mask a credit card number, showing only the last 4 digits.

    Args:
        card_number: The credit card number to mask

    Returns:
        A masked version of the credit card number or None if input was None
    """
    if card_number is None:
        return None

    if not card_number:
        return card_number

    # Remove any spaces or dashes from the card number
    cleaned_number = re.sub(r"[\s-]", "", card_number)

    # If too short, return as is
    if len(cleaned_number) < 10:
        logger.debug(f"Card number too short to mask: {len(cleaned_number)} digits")
        return card_number

    # Mask all but the last 4 digits
    return "*" * (len(cleaned_number) - 4) + cleaned_number[-4:]


def mask_email(email: Optional[str]) -> Optional[str]:
    """Mask an email address, showing only the first character of the username.

    Args:
        email: The email address to mask

    Returns:
        A masked version of the email or None if input was None
    """
    if email is None:
        return None

    if not email:
        return email

    # Simple regex for email validation
    email_pattern = r"^(.*?)@(.+)$"
    match = re.match(email_pattern, email)

    if not match:
        logger.debug(f"Not a valid email format: {email}")
        return email

    username, domain = match.groups()

    # If username is too short, return as is
    if len(username) <= 2:
        logger.debug(f"Email username too short to mask: {len(username)} characters")
        return email

    # Mask username except first character
    masked_username = username[0] + "*" * (len(username) - 1)
    return f"{masked_username}@{domain}"


def mask_phone_number(phone: Optional[str]) -> Optional[str]:
    """Mask a phone number, showing only the last 4 digits.

    Args:
        phone: The phone number to mask

    Returns:
        A masked version of the phone number or None if input was None
    """
    if phone is None:
        return None

    if not phone:
        return phone

    # Remove any non-digit characters
    digits_only = re.sub(r"\D", "", phone)

    # If too short, return as is
    if len(digits_only) < 7:
        logger.debug(f"Phone number too short to mask: {len(digits_only)} digits")
        return phone

    # Mask all but the last 4 digits
    return "*" * (len(digits_only) - 4) + digits_only[-4:]


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
    return re.sub(r"([a-f0-9]{8})[a-f0-9]*", r"\1****", key)
