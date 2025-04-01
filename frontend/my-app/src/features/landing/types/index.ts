/**
 * Types specific to the Landing page feature
 */
import { GenerationResponse } from '../../../types/concept.types';
import { FormStatus } from '../../../types/ui.types';

/**
 * Step model for the How It Works section
 */
export interface HowItWorksStep {
  number: number;
  title: string;
  description: string;
}

/**
 * Props for the HowItWorks component
 */
export interface HowItWorksProps {
  steps: HowItWorksStep[];
  onGetStarted: () => void;
}

/**
 * Recent concept model for display in RecentConcepts section
 */
export interface RecentConcept {
  id: string;
  title: string;
  description: string;
  colors: string[];
  gradient: {
    from: string;
    to: string;
  };
  initials: string;
}

/**
 * Props for the ResultsSection component
 */
export interface ResultsSectionProps {
  result: GenerationResponse;
  onReset: () => void;
  selectedColor: string | null;
  onColorSelect: (color: string) => void;
}

/**
 * Props for the ConceptFormSection component
 */
export interface ConceptFormSectionProps {
  onSubmit: (logoDescription: string, themeDescription: string) => void;
  status: FormStatus;
  error?: string;
  onReset: () => void;
}

/**
 * Props for the RecentConceptsSection component
 */
export interface RecentConceptsSectionProps {
  concepts: RecentConcept[];
  onEdit: (id: string) => void;
  onViewDetails: (id: string) => void;
} 