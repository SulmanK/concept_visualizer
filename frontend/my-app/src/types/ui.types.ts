/**
 * UI-related TypeScript interfaces for the Concept Visualizer application.
 */

/**
 * Common button variants
 */
export type ButtonVariant = "primary" | "secondary" | "outline" | "ghost";

/**
 * Common button sizes
 */
export type ButtonSize = "sm" | "md" | "lg";

/**
 * Common input field types
 */
export type InputType = "text" | "email" | "password" | "number" | "tel";

/**
 * Type for form submission status
 */
export type FormStatus = "idle" | "submitting" | "success" | "error";

/**
 * Concept data type
 */
export interface ConceptData {
  id: string;
  title: string;
  description: string;
  initials: string;
  colorVariations: string[][];
  images: {
    url: string;
    colors: string[];
  }[];
  onEdit: (conceptId: string, variationIndex?: number) => void;
  onViewDetails: (conceptId: string, variationIndex?: number) => void;
  onColorSelect: (color: string) => void;
  selectedColor: string | null;
}
