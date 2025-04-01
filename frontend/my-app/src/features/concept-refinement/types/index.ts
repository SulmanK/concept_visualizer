/**
 * Types specific to the Concept Refinement feature
 */
import { GenerationResponse } from '../../../types/concept.types';
import { FormStatus } from '../../../types/ui.types';

/**
 * Original concept model
 */
export interface OriginalConcept {
  imageUrl: string;
  logoDescription?: string;
  themeDescription?: string;
}

/**
 * Props for the RefinementForm component
 */
export interface RefinementFormProps {
  originalImageUrl: string;
  onSubmit: (
    refinementPrompt: string,
    logoDescription: string,
    themeDescription: string,
    preserveAspects: string[]
  ) => void;
  status: FormStatus;
  error?: string;
  onCancel: () => void;
  initialLogoDescription?: string;
  initialThemeDescription?: string;
}

/**
 * Props for the RefinementActions component
 */
export interface RefinementActionsProps {
  onReset: () => void;
  onCreateNew: () => void;
}

/**
 * Props for the ComparisonView component
 */
export interface ComparisonViewProps {
  originalConcept: OriginalConcept;
  refinedConcept: GenerationResponse;
  onColorSelect?: (color: string) => void;
  onRefineRequest?: () => void;
} 