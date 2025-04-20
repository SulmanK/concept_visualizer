# Format Utilities

The `formatUtils.ts` module provides a collection of utility functions for formatting various data types such as dates, numbers, currency, and file sizes into human-readable strings.

## Core Features

- Locale-aware date formatting
- Currency formatting with internationalization
- Number formatting with configurable decimal places
- File size conversion to human-readable units
- Consistent error handling for invalid inputs

## Key Functions

### formatDate

```typescript
formatDate(date: Date, locale = 'en-US'): string
```

Formats a date to a readable string (e.g., "Jan 1, 2023").

| Parameter | Type | Description |
|-----------|------|-------------|
| `date` | Date | Date to format |
| `locale` | string | Locale to use for formatting (defaults to 'en-US') |

### formatCurrency

```typescript
formatCurrency(amount: number, currency = 'USD', locale = 'en-US'): string
```

Formats a number as currency with proper symbol and thousands separators.

| Parameter | Type | Description |
|-----------|------|-------------|
| `amount` | number | Amount to format |
| `currency` | string | Currency code (defaults to 'USD') |
| `locale` | string | Locale to use for formatting (defaults to 'en-US') |

### formatNumber

```typescript
formatNumber(value: number, decimalPlaces = 2, locale = 'en-US'): string
```

Formats a number with thousand separators and a specified number of decimal places.

| Parameter | Type | Description |
|-----------|------|-------------|
| `value` | number | Number to format |
| `decimalPlaces` | number | Number of decimal places to include (defaults to 2) |
| `locale` | string | Locale to use for formatting (defaults to 'en-US') |

### formatFileSize

```typescript
formatFileSize(bytes: number, decimals = 2): string
```

Formats file size in bytes to a human-readable format (e.g., "1.5 MB").

| Parameter | Type | Description |
|-----------|------|-------------|
| `bytes` | number | File size in bytes |
| `decimals` | number | Number of decimal places to include (defaults to 2) |

## Usage Examples

### Formatting Dates

```typescript
import { formatDate } from '../utils/formatUtils';

const today = new Date();
const formattedDate = formatDate(today); // "Jan 1, 2023"
const frenchFormattedDate = formatDate(today, 'fr-FR'); // "1 janv. 2023"

// In a component
const DateDisplay = ({ timestamp }) => {
  const date = new Date(timestamp);
  return <span>{formatDate(date)}</span>;
};
```

### Formatting Currency

```typescript
import { formatCurrency } from '../utils/formatUtils';

const price = 1234.56;
const formattedPrice = formatCurrency(price); // "$1,234.56"
const euroPrice = formatCurrency(price, 'EUR'); // "€1,234.56"
const japaneseYen = formatCurrency(price, 'JPY', 'ja-JP'); // "¥1,235"

// In a component
const PriceDisplay = ({ amount }) => {
  return <span>{formatCurrency(amount)}</span>;
};
```

### Formatting File Sizes

```typescript
import { formatFileSize } from '../utils/formatUtils';

const fileSize = 1536; // bytes
const formattedSize = formatFileSize(fileSize); // "1.50 KB"
const sizeWithoutDecimals = formatFileSize(fileSize, 0); // "2 KB"
const largeFile = formatFileSize(1073741824); // "1.00 GB"

// In a component
const FileItem = ({ file }) => {
  return (
    <div>
      <span>{file.name}</span>
      <span>{formatFileSize(file.size)}</span>
    </div>
  );
};
```

## Implementation Notes

- All functions handle invalid inputs gracefully by returning empty strings
- The formatting functions use the native JavaScript `Intl` API for internationalization
- For file sizes, the functions use binary prefixes (powers of 1024) as is common in computing
- Special cases are handled for exact powers of 1024 to avoid unnecessary decimal places 