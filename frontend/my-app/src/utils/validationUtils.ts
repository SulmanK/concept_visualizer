/**
 * Check if a string is a valid email address
 *
 * @param email - Email address to validate
 * @returns True if the email is valid, false otherwise
 */
export function isValidEmail(email: string): boolean {
  if (!email) return false;

  // More strict email regex pattern to catch edge cases
  const emailRegex =
    /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+$/;
  return emailRegex.test(email);
}

/**
 * Check if a string is a valid password based on specified requirements
 *
 * @param password - Password to validate
 * @param minLength - Minimum password length (defaults to 8)
 * @param requireSpecialChar - Whether a special character is required (defaults to true)
 * @param requireNumber - Whether a number is required (defaults to true)
 * @param requireUppercase - Whether an uppercase letter is required (defaults to true)
 * @returns True if the password meets all requirements, false otherwise
 */
export function isValidPassword(
  password: string,
  minLength = 8,
  requireSpecialChar = true,
  requireNumber = true,
  requireUppercase = true,
): boolean {
  if (!password || password.length < minLength) return false;

  if (
    requireSpecialChar &&
    !/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]+/.test(password)
  ) {
    return false;
  }

  if (requireNumber && !/\d/.test(password)) {
    return false;
  }

  if (requireUppercase && !/[A-Z]/.test(password)) {
    return false;
  }

  return true;
}

/**
 * Check if a string is a valid URL
 *
 * @param url - URL to validate
 * @param requireProtocol - Whether the protocol (http/https) is required (defaults to true)
 * @returns True if the URL is valid, false otherwise
 */
export function isValidUrl(url: string, requireProtocol = true): boolean {
  if (!url) return false;

  try {
    const urlObj = new URL(url);
    if (requireProtocol && !["http:", "https:"].includes(urlObj.protocol)) {
      return false;
    }
    return true;
  } catch (error) {
    return false;
  }
}

/**
 * Check if a string contains only alphanumeric characters
 *
 * @param str - String to validate
 * @param allowSpaces - Whether spaces are allowed (defaults to false)
 * @returns True if the string contains only alphanumeric characters, false otherwise
 */
export function isAlphanumeric(str: string, allowSpaces = false): boolean {
  if (!str) return false;

  const pattern = allowSpaces ? /^[a-zA-Z0-9\s]*$/ : /^[a-zA-Z0-9]*$/;
  return pattern.test(str);
}

/**
 * Check if a value is within a specified range
 *
 * @param value - Numeric value to check
 * @param min - Minimum allowed value (inclusive)
 * @param max - Maximum allowed value (inclusive)
 * @returns True if the value is within the range, false otherwise
 */
export function isInRange(value: number, min: number, max: number): boolean {
  if (typeof value !== "number" || isNaN(value)) return false;
  return value >= min && value <= max;
}
