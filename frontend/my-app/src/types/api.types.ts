/**
 * API-related TypeScript interfaces for the Concept Visualizer application.
 */

/**
 * API Error response model
 */
export interface ApiError {
  status: number;
  message: string;
  details?: string;
}

/**
 * Common API response wrapper
 */
export interface ApiResponse<T> {
  data?: T;
  error?: ApiError;
  loading: boolean;
}

/**
 * Task status type
 */
export type TaskStatus = "pending" | "processing" | "completed" | "failed";

/**
 * Task response model
 */
export interface TaskResponse {
  id: string;
  task_id?: string;
  status: TaskStatus;
  type: "generate_concept" | "refine_concept";
  result_id?: string;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

/**
 * Request model for concept generation
 */
export interface PromptRequest {
  logo_description: string;
  theme_description: string;
}

/**
 * Request model for concept refinement
 */
export interface RefinementRequest {
  original_image_url: string;
  logo_description?: string;
  theme_description?: string;
  refinement_prompt: string;
  preserve_aspects: string[];
}
