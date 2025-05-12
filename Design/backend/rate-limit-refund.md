# Rate Limit Refund Design Document

## Problem Statement

When a user attempts to submit a task while they already have a task in progress, the system returns a 409 Conflict error. Currently, this still consumes one of the user's rate-limited attempts, which creates a poor user experience. Users should not lose a rate-limited attempt when the system rejects their request due to an active task.

## Requirements

1. Modify the rate limit middleware to track which rate limits were applied to a request
2. Implement a mechanism to refund rate limits when a 409 Conflict occurs
3. Ensure the refund process is robust and handles error cases gracefully
4. Add appropriate logging for monitoring and debugging

## Design

### Overview

The implementation will follow a three-part approach:

1. Modify the `RateLimitApplyMiddleware` to store information about applied limits on the request state
2. Update the task creation endpoints to check for 409 Conflict conditions and refund applied rate limits
3. Implement a `decrement_specific_limit` method in the `RedisStore` class to handle the refund

### Detailed Design

#### 1. Modify RateLimitApplyMiddleware

The middleware will store information about which rate limits were successfully applied to a request:

```python
# Store applied limits in request.state for potential refund
request.state.applied_rate_limits_for_refund = [
    {
        "user_id": user_id,
        "endpoint_rule": endpoint_rule,
        "limit_string_rule": rate_limit_string,
        "amount": 1
    }
    # Could be multiple items if multiple limits were applied
]
```

#### 2. Update Task Creation Endpoints

When a 409 Conflict is detected, the endpoint will:

- Check for applied rate limits in the request state
- Obtain the RedisStore instance
- Call the decrement method for each applied limit
- Log success or failure
- Return the 409 response

#### 3. Implement decrement_specific_limit in RedisStore

This method will:

- Reconstruct the Redis key based on user_id, endpoint_rule, and limit_string_rule
- Check if the key exists and has a positive value
- Decrement the key by the specified amount
- Handle edge cases and errors

### Implementation Plan

1. First Phase:

   - Implement the RedisStore.decrement_specific_limit method
   - Write unit tests for this method

2. Second Phase:

   - Modify RateLimitApplyMiddleware to store applied limits
   - Add integration tests for the middleware changes

3. Third Phase:
   - Update task endpoints to refund rate limits on 409 Conflict
   - Add integration tests for the complete flow

### Testing Strategy

- Unit tests for RedisStore.decrement_specific_limit
- Integration tests for the RateLimitApplyMiddleware changes
- End-to-end tests for the complete flow (request → 409 → refund)
- Test error handling for cases where refund fails

### Monitoring

- Add DEBUG level logs for successful refunds
- Add WARNING level logs for refund attempts with no applied limits
- Add ERROR level logs for failed refunds
- Consider adding metrics for tracking successful/failed refunds

## Limitations

This implementation only handles refunds for 409 Conflict scenarios. It does not handle:

- Refunds for worker failures
- Refunds for other types of task failures
- Refunds for stuck tasks

These more complex scenarios may be addressed in future iterations if they prove to be significant issues.
