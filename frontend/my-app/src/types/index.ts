/**
 * Re-export all types from domain-specific files
 */

// API Types
export * from "./api.types";

// Concept Types
export * from "./concept.types";

// UI Types
export * from "./ui.types";

// Form Types
export * from "./form.types";

// Error Types
export * from "./error.types";

/**
 * Form status type
 */
export type FormStatus =
  | "idle"
  | "submitting"
  | "initiating"
  | "pending"
  | "processing"
  | "success"
  | "error";
