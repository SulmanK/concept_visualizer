# Utils

This directory contains utility functions and helper modules used throughout the Concept Visualizer application. These utilities provide reusable functionality for common tasks such as formatting, validation, error handling, and logging.

## Directory Structure

Utilities are organized by functionality:

- **dev-logging.ts**: Development-only logging utilities
- **errorUtils.ts**: Error handling and processing utilities
- **formatUtils.ts**: Formatting functions for dates, numbers, and strings
- **logger.ts**: Production-safe logging utilities
- **stringUtils.ts**: String manipulation and processing utilities
- **url.ts**: URL handling and manipulation utilities
- **validationUtils.ts**: Input validation utilities

## Key Utility Modules

### Error Utilities

The `errorUtils.ts` module provides functions for consistent error handling:

- **parseApiError**: Extracts meaningful error messages from API responses
- **isNetworkError**: Checks if an error is a network connectivity issue
- **formatErrorForUser**: Formats error messages for display to users
- **createErrorHandler**: Creates a standardized error handler for async operations

### Logging Utilities

The logging utilities provide consistent logging with appropriate levels:

- **logger.info**: Logs informational messages in production
- **logger.warn**: Logs warning messages
- **logger.error**: Logs error messages with error details
- **dev.log**: Development-only logging that's stripped in production

### Format Utilities

The `formatUtils.ts` module provides formatting functions:

- **formatDate**: Formats dates in various formats
- **formatFileSize**: Formats byte sizes as human-readable strings
- **formatDuration**: Formats durations in milliseconds as readable time
- **truncateString**: Truncates strings with ellipsis

### Validation Utilities

The `validationUtils.ts` module provides input validation functions:

- **isValidEmail**: Validates email addresses
- **isValidPassword**: Validates password strength
- **isValidUrl**: Validates URL format
- **validateConceptInput**: Validates concept generation input

## Usage Examples

### Error Handling

```typescript
import { parseApiError, createErrorHandler } from '../utils/errorUtils';
import { logger } from '../utils/logger';

const fetchData = async () => {
  try {
    const response = await api.get('/data');
    return response.data;
  } catch (error) {
    const errorMessage = parseApiError(error);
    logger.error('Failed to fetch data', { error: errorMessage });
    throw new Error(errorMessage);
  }
};

// Or using the error handler creator
const handleError = createErrorHandler('Failed to fetch data');

const fetchDataSafe = async () => {
  try {
    const response = await api.get('/data');
    return response.data;
  } catch (error) {
    handleError(error);
  }
};
```

### Formatting

```typescript
import { formatDate, truncateString } from '../utils/formatUtils';

const FormattedDate = ({ date }) => {
  return <span>{formatDate(date, 'MMM DD, YYYY')}</span>;
};

const TruncatedText = ({ text, maxLength = 100 }) => {
  return <p>{truncateString(text, maxLength)}</p>;
};
```

### Validation

```typescript
import { isValidEmail, validateConceptInput } from '../utils/validationUtils';

const validateForm = (formData) => {
  const errors = {};
  
  if (!isValidEmail(formData.email)) {
    errors.email = 'Please enter a valid email address';
  }
  
  const conceptErrors = validateConceptInput(formData.logoDescription, formData.themeDescription);
  if (conceptErrors) {
    errors.logoDescription = conceptErrors.logoDescription;
    errors.themeDescription = conceptErrors.themeDescription;
  }
  
  return Object.keys(errors).length > 0 ? errors : null;
};
```

## Best Practices

1. **Pure Functions**: Keep utility functions pure when possible
2. **Error Handling**: Provide clear error messages and consistent error handling
3. **Type Safety**: Use TypeScript types for parameters and return values
4. **Documentation**: Document utility functions with JSDoc comments
5. **Testing**: Write unit tests for utility functions
6. **Consistency**: Maintain consistent naming and parameter order
7. **Single Responsibility**: Each utility file should focus on a specific domain 