/**
 * API Endpoint constants
 *
 * This file contains all API endpoint paths used throughout the application
 * to ensure consistency and ease of maintenance.
 */

/**
 * Default interval in milliseconds for polling operations (e.g., task status checks)
 */
export const DEFAULT_POLLING_INTERVAL = 2000; // 2 seconds

/**
 * Task status endpoint base path
 */
export const TASK_STATUS = {
  /** Base path for task endpoints */
  BASE_PATH: "tasks",
  /** Task is waiting to be processed */
  PENDING: "pending",
  /** Task is currently being processed */
  PROCESSING: "processing",
  /** Task has been completed successfully */
  COMPLETED: "completed",
  /** Task has failed */
  FAILED: "failed",
  /** Task has been canceled */
  CANCELED: "canceled",
};

export const API_ENDPOINTS = {
  GENERATE_CONCEPT: "concepts/generate-with-palettes",
  REFINE_CONCEPT: "concepts/refine",
  TASK_STATUS_BY_ID: (taskId: string) => `${TASK_STATUS.BASE_PATH}/${taskId}`,
  TASK_CANCEL: (taskId: string) => `${TASK_STATUS.BASE_PATH}/${taskId}/cancel`,
  EXPORT_IMAGE: "export/process",
  RECENT_CONCEPTS: "storage/recent",
  CONCEPT_DETAIL: (id: string) => `storage/concept/${id}`,
  RATE_LIMITS: "health/rate-limits-status",
};
