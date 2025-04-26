/**
 * Error-related TypeScript interfaces for the Concept Visualizer application.
 */

/**
 * Error categories enumeration
 */
export type ErrorCategory =
  | "network"
  | "auth"
  | "validation"
  | "rateLimit"
  | "api"
  | "server"
  | "unknown";

/**
 * Basic application debug info
 */
export interface DebugInfo {
  environment: string;
  apiBaseUrl: string;
  supabaseUrl: string;
  [key: string]: string | number | boolean;
}

/**
 * Validation error structure
 */
export interface ValidationError {
  field: string;
  message: string;
}

/**
 * Rate limit data structure
 */
export interface RateLimitData {
  limit: number;
  current: number;
  period: string;
  resetAfterSeconds: number;
}

/**
 * Common application error interface
 */
export interface ApplicationError {
  message: string;
  details?: string;
  category: ErrorCategory;
  status?: number;
  validationErrors?: ValidationError[];
  limit?: number;
  current?: number;
  period?: string;
  resetAfterSeconds?: number;
}
