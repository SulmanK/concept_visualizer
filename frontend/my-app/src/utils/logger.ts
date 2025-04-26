/**
 * Logger utility that conditionally logs based on environment
 *
 * In production, debug and info logs are suppressed
 * Warnings and errors are always shown
 */

// Check if we're in development mode
const isDev = import.meta.env.DEV === true;

/**
 * Logger interface with methods for different log levels
 */
interface Logger {
  debug: (message: string, ...args: unknown[]) => void;
  info: (message: string, ...args: unknown[]) => void;
  warn: (message: string, ...args: unknown[]) => void;
  error: (message: string, ...args: unknown[]) => void;
}

/**
 * Production logger - suppresses debug and info logs
 */
const productionLogger: Logger = {
  debug: () => {},
  info: () => {},
  warn: console.warn.bind(console),
  error: console.error.bind(console),
};

/**
 * Development logger - shows all logs
 */
const developmentLogger: Logger = {
  debug: console.debug.bind(console),
  info: console.info.bind(console),
  warn: console.warn.bind(console),
  error: console.error.bind(console),
};

/**
 * Logger instance based on environment
 */
export const logger: Logger = isDev ? developmentLogger : productionLogger;

/**
 * Helper function to log only in development environments
 */
export function logDev(message: string, ...args: unknown[]) {
  if (isDev) {
    console.log(message, ...args);
  }
}
