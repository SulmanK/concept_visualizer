# Health API Utilities

This documentation covers the utility functions used by health check and rate limit endpoints in the Concept Visualizer API.

## Overview

The `utils.py` module provides helper functions that are used by the health and rate limit endpoints. These utilities help with:

- Calculating rate limit reset times
- Masking sensitive information in logs (IPs, user IDs)
- Formatting data for health check responses

## Utility Functions

### Rate Limit Utilities

#### get_reset_time

```python
def get_reset_time(period: str) -> int:
    """Calculate approximate reset time in seconds."""
```

This function calculates the approximate time until a rate limit period resets, based on the current time:

- `minute`: Seconds until the next minute
- `hour`: Seconds until the next hour
- `day`: Seconds until midnight
- `month`: Seconds until the 1st of the next month

**Example:**

```python
# If it's 3:45:30 PM
seconds_until_reset = get_reset_time("hour")  # Returns 870 (14 minutes and 30 seconds)
```

### Privacy Utilities

These functions mask sensitive information for logging and responses:

#### mask_ip

```python
def mask_ip(ip_address: str) -> str:
    """Mask an IP address for privacy in logs."""
```

Obscures IP addresses to protect user privacy:

- IPv4: `192.168.**.**`
- IPv6: `2001:****:****`

**Example:**

```python
masked = mask_ip("192.168.1.100")  # Returns "192.168.**.**"
```

#### mask_id

```python
def mask_id(id_value: str) -> str:
    """Mask an identifier (user ID or IP) for privacy in logs."""
```

Obscures different types of identifiers:

- User IDs: `user:1234****`
- IPs: `ip:192.168.**.**`
- Other IDs: First 4 characters followed by asterisks

**Example:**

```python
masked_user = mask_id("user:1234567890")  # Returns "user:1234******"
masked_ip = mask_id("ip:192.168.1.100")   # Returns "ip:192.168.**.**"
```

#### mask_key

```python
def mask_key(key: str) -> str:
    """Mask a Redis key that might contain sensitive information."""
```

Masks Redis keys that might contain sensitive information like user IDs or IP addresses.

**Example:**

```python
masked = mask_key("rate-limit:user:1234567890:generate")  # Returns "rate-limit:user:1234******:generate"
```

## Usage Examples

### Calculating Rate Limit Headers

```python
from app.api.routes.health.utils import get_reset_time

# Get the rate limit period from configuration
period = "hour"  # Could be minute, hour, day, month

# Calculate reset time
reset_seconds = get_reset_time(period)

# Add to current Unix timestamp to get absolute reset time
import time
reset_at = int(time.time()) + reset_seconds

# Add to response headers
headers = {
    "X-RateLimit-Reset": str(reset_at)
}
```

### Privacy-Conscious Logging

```python
import logging
from app.api.routes.health.utils import mask_ip, mask_id

logger = logging.getLogger("api")

def log_request(user_id: str, ip_address: str):
    """Log request details with privacy measures."""
    masked_user = mask_id(user_id) if user_id else "anonymous"
    masked_ip = mask_ip(ip_address)

    logger.info(f"Request from {masked_user} ({masked_ip})")
```

## Security Considerations

The utility functions in this module help implement privacy-by-design principles:

- User IDs are always masked in logs to prevent exposure of personal identifiers
- IP addresses are partially obscured to balance logging needs with privacy
- Redis keys are masked to prevent sensitive data from appearing in logs

These measures help comply with privacy regulations like GDPR while still maintaining useful logging for debugging and monitoring.

## Related Files

- [Health Endpoints](endpoints.md): Basic health check endpoints
- [Rate Limits](limits.md): Rate limit information endpoints
- [API Middleware](../../middleware/rate_limit_headers.md): Rate limit headers middleware
