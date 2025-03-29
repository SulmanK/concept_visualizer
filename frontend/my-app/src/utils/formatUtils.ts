/**
 * Format a date to a readable string (e.g., "Jan 1, 2023")
 * 
 * @param date - Date to format
 * @param locale - Locale to use for formatting (defaults to 'en-US')
 * @returns Formatted date string
 */
export function formatDate(date: Date, locale = 'en-US'): string {
  if (!date || !(date instanceof Date) || isNaN(date.getTime())) {
    return '';
  }
  
  return date.toLocaleDateString(locale, {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });
}

/**
 * Format a number as currency
 * 
 * @param amount - Amount to format
 * @param currency - Currency code (defaults to 'USD')
 * @param locale - Locale to use for formatting (defaults to 'en-US')
 * @returns Formatted currency string
 */
export function formatCurrency(amount: number, currency = 'USD', locale = 'en-US'): string {
  if (typeof amount !== 'number' || isNaN(amount)) {
    return '';
  }
  
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency
  }).format(amount);
}

/**
 * Format a number with thousand separators and decimal places
 * 
 * @param value - Number to format
 * @param decimalPlaces - Number of decimal places to include (defaults to 2)
 * @param locale - Locale to use for formatting (defaults to 'en-US')
 * @returns Formatted number string
 */
export function formatNumber(value: number, decimalPlaces = 2, locale = 'en-US'): string {
  if (typeof value !== 'number' || isNaN(value)) {
    return '';
  }
  
  return new Intl.NumberFormat(locale, {
    minimumFractionDigits: decimalPlaces,
    maximumFractionDigits: decimalPlaces
  }).format(value);
}

/**
 * Format file size in bytes to human-readable format (e.g., "1.5 MB")
 * 
 * @param bytes - File size in bytes
 * @param decimals - Number of decimal places to include (defaults to 2)
 * @returns Formatted file size string
 */
export function formatFileSize(bytes: number, decimals = 2): string {
  if (bytes === 0) return '0 Bytes';
  if (typeof bytes !== 'number' || isNaN(bytes) || bytes < 0) return '';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  // Calculate the size value
  const sizeValue = bytes / Math.pow(k, i);
  
  // Special case for exact powers of 1024 with no decimals specified
  if (sizeValue === 1 && bytes % Math.pow(k, i) === 0 && decimals === 2) {
    return `1 ${sizes[i]}`;
  } else if (decimals === 0) {
    // If decimals is 0, round to nearest integer
    return `${Math.round(sizeValue)} ${sizes[i]}`;
  } else {
    // Otherwise, use the fixed decimal places
    return `${sizeValue.toFixed(decimals)} ${sizes[i]}`;
  }
} 