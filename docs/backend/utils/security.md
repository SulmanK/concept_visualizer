# Security Utilities

The `app.utils.security` module provides functions to enhance security throughout the application, particularly for masking sensitive information in logs and error messages.

## Key Functions

### `mask_id`

```python
def mask_id(id_value: Optional[str], visible_chars: int = 8) -> str
```

Mask an ID (session ID, concept ID, etc.) to protect privacy in logs.

**Parameters:**

- `id_value`: The ID to mask
- `visible_chars`: Number of characters to show before masking

**Returns:**

- Masked ID showing only the first few characters followed by asterisks

**Example Usage:**

```python
from app.utils.security import mask_id

# Mask a session ID
session_id = "abcdef1234567890"
masked = mask_id(session_id)  # Returns "abcdef12***"

# Mask with fewer visible characters
masked = mask_id(session_id, visible_chars=4)  # Returns "abcd***"
```

### `mask_path`

```python
def mask_path(path: Optional[str]) -> str
```

Mask a storage path to protect session ID privacy.

**Parameters:**

- `path`: Storage path potentially containing session ID

**Returns:**

- Masked path with session ID portion obscured

**Example Usage:**

```python
from app.utils.security import mask_path

# Mask a storage path
path = "session_123456789/images/logo.png"
masked = mask_path(path)  # Returns "session_12***/images/logo.png"
```

### `mask_ip`

```python
def mask_ip(ip_address: Optional[str]) -> str
```

Mask an IP address to protect privacy in logs.

**Parameters:**

- `ip_address`: The IP address to mask

**Returns:**

- Masked IP address showing only parts of the address

**Example Usage:**

```python
from app.utils.security import mask_ip

# Mask an IPv4 address
masked = mask_ip("192.168.1.1")  # Returns "192.168.*.*"

# Mask an IPv6 address
masked = mask_ip("2001:db8::1428:57ab")  # Returns "2001:db8:****"
```

### `mask_redis_key`

```python
def mask_redis_key(key: Optional[str]) -> str
```

Mask a Redis key that might contain sensitive information.

**Parameters:**

- `key`: Redis key to mask

**Returns:**

- Masked Redis key with sensitive parts obscured

**Example Usage:**

```python
from app.utils.security import mask_redis_key

# Mask a session key
masked = mask_redis_key("session:abc123def456")  # Returns "session:abc123**"

# Mask a rate limit key
masked = mask_redis_key("rate-limit:api:user:12345")  # Returns "rate-limit:api:user:12***"
```

## Implementation Details

The masking utilities apply different masking strategies based on the type of data:

- **IDs**: Show first N characters, replace the rest with asterisks
- **Paths**: Mask the session ID part but keep the file path structure
- **IP Addresses**: 
  - IPv4: Show first two octets, mask the rest
  - IPv6: Show first two segments, mask the rest
- **Redis Keys**: Identify key type and apply appropriate masking pattern

These utilities should be used in all logging statements that might contain sensitive information. 