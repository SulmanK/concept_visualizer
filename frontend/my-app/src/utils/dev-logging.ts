/**
 * Utility for conditionally logging based on the environment
 *
 * This module creates wrapper functions that only log in development mode,
 * keeping the production console clean.
 */

// Check if we're in development mode
const isDev = import.meta.env.DEV === true;

/**
 * Log to console only in development mode
 */
export function devLog(...args: any[]): void {
  if (isDev) {
    console.log(...args);
  }
}

/**
 * Log warnings to console only in development mode
 */
export function devWarn(...args: any[]): void {
  if (isDev) {
    console.warn(...args);
  }
}

/**
 * Log debug information to console only in development mode
 */
export function devDebug(...args: any[]): void {
  if (isDev) {
    console.debug(...args);
  }
}

/**
 * Log info to console only in development mode
 */
export function devInfo(...args: any[]): void {
  if (isDev) {
    console.info(...args);
  }
}

/**
 * Always log errors to console regardless of environment
 * This ensures critical errors are visible in all environments
 */
export function logError(...args: any[]): void {
  console.error(...args);
}
