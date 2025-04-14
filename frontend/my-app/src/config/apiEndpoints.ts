/**
 * API Endpoint Constants
 * 
 * This file contains centralized constants for all API endpoints used in the application.
 * Using these constants instead of hardcoded strings ensures consistency and makes
 * refactoring easier.
 */

export const API_ENDPOINTS = {
  // Concept related endpoints
  GENERATE_CONCEPT: '/concepts/generate-with-palettes',
  REFINE_CONCEPT: '/concepts/refine',
  RECENT_CONCEPTS: '/storage/recent',
  CONCEPT_DETAIL: (id: string) => `/storage/concept/${id}`,
  
  // Task related endpoints
  TASK_STATUS: (taskId: string) => `/tasks/${taskId}`,
  TASK_CANCEL: (taskId: string) => `/tasks/${taskId}/cancel`,
  
  // Export related endpoints
  EXPORT_IMAGE: '/export/process',
  
  // Health and rate limits
  HEALTH_CHECK: '/health',
  RATE_LIMITS: '/health/rate-limits-status',
};

// Default time values
export const DEFAULT_POLLING_INTERVAL = 2000; // 2 seconds
export const DEFAULT_TOAST_DURATION = 5000; // 5 seconds

// HTTP Status Codes
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  ACCEPTED: 202,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  UNPROCESSABLE_ENTITY: 422,
  TOO_MANY_REQUESTS: 429,
  INTERNAL_SERVER_ERROR: 500,
  SERVICE_UNAVAILABLE: 503,
};

// Task Status Constants
export const TASK_STATUS = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed',
  CANCELED: 'canceled',
};

// Task Types
export const TASK_TYPE = {
  CONCEPT_GENERATION: 'concept_generation',
  CONCEPT_REFINEMENT: 'concept_refinement',
}; 