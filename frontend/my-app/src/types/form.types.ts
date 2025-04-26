/**
 * Form-related TypeScript interfaces for the Concept Visualizer application.
 */

/**
 * Concept generation form data structure
 */
export interface ConceptFormData {
  logoDescription: string;
  themeDescription: string;
}

/**
 * Concept refinement form data structure
 */
export interface RefinementFormData {
  logoDescription: string;
  themeDescription: string;
  refinementPrompt: string;
  preserveAspects: string[];
}

/**
 * Props for form validation
 */
export interface ValidationProps {
  value: string;
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
}

/**
 * Error state for form validation
 */
export interface FormErrors {
  [key: string]: string;
}
